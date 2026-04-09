#!/usr/bin/env python3
"""
Ingest a source document into the LLM Wiki.

Usage:
    python tools/ingest.py <path-to-source> --kb <name>

The LLM reads the source, extracts knowledge, and updates the wiki:
  - Creates wiki/sources/<slug>.md
  - Updates wiki/index.md
  - Updates wiki/overview.md (if warranted)
  - Creates/updates entity and concept pages
  - Appends to wiki/log.md
  - Flags contradictions
  - Updates tree/index.json with new tree nodes
"""

import os
import sys
import json
import hashlib
import re
import shutil
import argparse
from pathlib import Path
from datetime import date

import anthropic

REPO_ROOT = Path(__file__).parent.parent
SCHEMA_FILE = REPO_ROOT / "CLAUDE.md"
META_FILE = REPO_ROOT / "meta.json"


def resolve_kb_path(kb_name: str | None) -> tuple[Path, Path, Path, Path]:
    """解析知识库路径，返回 (kb_path, wiki_dir, raw_dir, tree_file)"""
    if META_FILE.exists():
        meta = json.loads(META_FILE.read_text())
    else:
        meta = {"default": None}

    if kb_name is None:
        kb_name = meta.get("default")

    if not kb_name:
        print("Error: no knowledge base specified and no default set.")
        print("Use --kb <name>")
        sys.exit(1)

    kb_path = REPO_ROOT / "knowledge_bases" / kb_name
    if not kb_path.exists():
        print(f"Error: knowledge base not found: {kb_name}")
        sys.exit(1)

    wiki_dir = kb_path / "wiki"
    raw_dir = kb_path / "raw"
    tree_file = kb_path / "tree" / "index.json"
    return kb_path, wiki_dir, raw_dir, tree_file


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_file(path: Path, content: str, merge: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if merge and path.exists():
        # Merge: append new connections/quotes to existing content
        existing = path.read_text(encoding="utf-8")
        merged = merge_page_content(existing, content)
        path.write_text(merged, encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")
    print(f"  wrote: {path.relative_to(REPO_ROOT)}")


def merge_page_content(existing: str, new: str) -> str:
    """Merge new content into existing entity/concept page. Appends new claims/quotes."""
    # Extract existing content sections
    # For simplicity: if page exists, append new content under a second "## New Sources" header
    if "## Key Claims" in new and "## Key Claims" in existing:
        # Extract claims from new
        new_claims_match = re.search(r"(## Key Claims\n[\s\S]*?)(?=\n## |$)", new)
        if new_claims_match:
            new_claims = new_claims_match.group(1).strip()
            # Remove first "## Key Claims" header from new claims, keep bullet points
            new_claims_body = re.sub(r"^## Key Claims\n", "", new_claims)
            if new_claims_body.strip():
                existing = existing.rstrip() + "\n\n## Key Claims (additional)\n" + new_claims_body
    if "## Connections" in new and "## Connections" in existing:
        new_conn_match = re.search(r"(## Connections\n[\s\S]*?)(?=\n## |$)", new)
        if new_conn_match:
            new_conn_body = re.sub(r"^## Connections\n", "", new_conn_match.group(1))
            if new_conn_body.strip():
                existing = existing.rstrip() + "\n\n## Connections (additional)\n" + new_conn_body
    return existing


def get_manifest(kb_path: Path) -> dict:
    """Load or initialize the ingest manifest."""
    manifest_file = kb_path / "wiki" / ".ingest-manifest.json"
    if manifest_file.exists():
        return json.loads(manifest_file.read_text())
    return {}


def save_manifest(kb_path: Path, manifest: dict):
    """Save the ingest manifest."""
    manifest_file = kb_path / "wiki" / ".ingest-manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))


def mark_ingested(kb_path: Path, source: Path, source_hash: str, slug: str, title: str):
    """Record this source as successfully ingested. Uses relative path as key to avoid name collisions."""
    manifest = get_manifest(kb_path)
    # Use relative path from kb root as key (e.g. "docs/rag.md"), not just filename
    try:
        rel_path = str(source.resolve().relative_to(kb_path.resolve()))
    except ValueError:
        rel_path = source.name
    manifest[rel_path] = {
        "hash": source_hash,
        "slug": slug,
        "title": title,
        "source_name": source.name
    }
    save_manifest(kb_path, manifest)


def build_wiki_context() -> str:
    parts = []
    if INDEX_FILE.exists():
        parts.append(f"## wiki/index.md\n{read_file(INDEX_FILE)}")
    if OVERVIEW_FILE.exists():
        parts.append(f"## wiki/overview.md\n{read_file(OVERVIEW_FILE)}")
    # Include a few recent source pages for contradiction checking
    sources_dir = WIKI_DIR / "sources"
    if sources_dir.exists():
        recent = sorted(sources_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        for p in recent:
            parts.append(f"## {p.relative_to(REPO_ROOT)}\n{p.read_text()}")
    return "\n\n---\n\n".join(parts)


def update_tree_index(tree_node: dict, kb_path: Path):
    """Update tree/index.json with new tree nodes. Idempotent: skips if leaf already exists."""
    tree_file = kb_path / "tree" / "index.json"

    if tree_file.exists():
        try:
            tree_data = json.loads(tree_file.read_text())
        except json.JSONDecodeError:
            tree_data = {"name": "root", "description": "Knowledge base root", "children": []}
    else:
        tree_data = {"name": "root", "description": "Knowledge base root", "children": []}

    topic_path = tree_node.get("topic_path", [])
    sections = tree_node.get("sections", [])
    slug = tree_node.get("slug", "")
    raw_path = f"raw/{slug}.md" if slug else f"raw/{kb_path.name}.md"

    # Navigate or create the topic path
    current_level = tree_data["children"]
    for topic_name in topic_path:
        # Find or create this topic
        found = None
        for child in current_level:
            if child.get("name") == topic_name and child.get("type") == "topic":
                found = child
                break
        if found:
            current_level = found["children"]
        else:
            # Create new topic node
            new_topic = {
                "name": topic_name,
                "description": tree_node.get("description", ""),
                "keywords": tree_node.get("keywords", []),
                "type": "topic",
                "children": []
            }
            current_level.append(new_topic)
            current_level = new_topic["children"]

    # Skip if this leaf already exists under this parent
    for existing in current_level:
        if existing.get("name") == raw_path and existing.get("type") == "leaf":
            print(f"  (tree leaf {raw_path} already exists — skipping)")
            return

    # Add the leaf node for this document
    leaf_node = {
        "name": raw_path,
        "type": "leaf",
        "sections": sections
    }
    current_level.append(leaf_node)

    # Write back
    tree_file.parent.mkdir(parents=True, exist_ok=True)
    tree_file.write_text(json.dumps(tree_data, indent=2, ensure_ascii=False))
    print(f"  updated tree: added leaf under {'/'.join(topic_path)}")


def parse_json_from_response(text: str) -> dict:
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    # Find the outermost JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in response")
    return json.loads(match.group())


def update_index(new_entry: str, slug: str, section: str = "Sources"):
    """Add entry to index if slug is not already present."""
    content = read_file(INDEX_FILE)
    if not content:
        content = "# Wiki Index\n\n## Overview\n- [Overview](overview.md) — living synthesis\n\n## Sources\n\n## Entities\n\n## Concepts\n\n## Syntheses\n"
    # Skip if this slug is already indexed
    if f"sources/{slug}.md" in content:
        print(f"  (index entry for {slug} already exists — skipping)")
        return
    section_header = f"## {section}"
    if section_header in content:
        content = content.replace(section_header + "\n", section_header + "\n" + new_entry + "\n")
    else:
        content += f"\n{section_header}\n{new_entry}\n"
    write_file(INDEX_FILE, content)


def append_log(entry: str):
    existing = read_file(LOG_FILE)
    write_file(LOG_FILE, entry.strip() + "\n\n" + existing)


def extract_text_from_content(content_blocks: list) -> str:
    """Extract text from API response content, handling ThinkingBlocks."""
    texts = []
    for block in content_blocks:
        if hasattr(block, 'text'):
            texts.append(block.text)
        elif hasattr(block, 'thinking'):
            pass  # Skip thinking blocks
    return "\n".join(texts)


def ingest(source_path: str, kb_path: Path, wiki_dir: Path, raw_dir: Path, tree_file: Path):
    global WIKI_DIR, RAW_DIR, TREE_FILE, INDEX_FILE, OVERVIEW_FILE, LOG_FILE
    WIKI_DIR = wiki_dir
    RAW_DIR = raw_dir
    TREE_FILE = tree_file
    INDEX_FILE = wiki_dir / "index.md"
    OVERVIEW_FILE = wiki_dir / "overview.md"
    LOG_FILE = wiki_dir / "log.md"

    source = Path(source_path)
    if not source.exists():
        print(f"Error: file not found: {source_path}")
        sys.exit(1)

    source_content = source.read_text(encoding="utf-8")
    source_hash = sha256(source_content)
    today = date.today().isoformat()

    # Idempotency check — skip if this exact source was already ingested
    manifest = get_manifest(kb_path)
    try:
        rel_path = str(source.resolve().relative_to(kb_path.resolve()))
    except ValueError:
        rel_path = source.name
    entry = manifest.get(rel_path)
    if entry is not None and entry.get("hash") == source_hash:
        print(f"\nSkipping: {source.name}  (hash: {source_hash})")
        print(f"  Already ingested as '{entry['slug']}' — source unchanged.")
        return

    # Copy source to raw/ if it's not already there
    dest_in_raw = raw_dir / source.name
    if not dest_in_raw.exists() or dest_in_raw.read_text() != source.read_text():
        raw_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest_in_raw)
        print(f"  copied to: {dest_in_raw.relative_to(REPO_ROOT)}")

    print(f"\nIngesting: {source.name}  (hash: {source_hash})")

    wiki_context = build_wiki_context()
    schema = read_file(SCHEMA_FILE)

    client = anthropic.Anthropic(
        base_url=os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
        api_key=os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY"),
    )

    prompt = f"""You are maintaining an LLM Wiki. Process this source document and integrate its knowledge into the wiki.

Schema and conventions:
{schema}

Current wiki state (index + recent pages):
{wiki_context if wiki_context else "(wiki is empty — this is the first source)"}

New source to ingest (file: {source.relative_to(REPO_ROOT) if source.is_relative_to(REPO_ROOT) else source.name}):
=== SOURCE START ===
{source_content}
=== SOURCE END ===

Today's date: {today}

Return ONLY a valid JSON object with these fields (no markdown fences, no prose outside the JSON):
{{
  "title": "Human-readable title for this source",
  "slug": "kebab-case-slug-for-filename",
  "source_page": "full markdown content for wiki/sources/<slug>.md — use the source page format from the schema",
  "index_entry": "- [Title](sources/slug.md) — one-line summary",
  "overview_update": "full updated content for wiki/overview.md, or null if no update needed",
  "entity_pages": [
    {{"path": "entities/EntityName.md", "content": "full markdown content"}}
  ],
  "concept_pages": [
    {{"path": "concepts/ConceptName.md", "content": "full markdown content"}}
  ],
  "contradictions": ["describe any contradiction with existing wiki content, or empty list"],
  "log_entry": "## [{today}] ingest | <title>\\n\\nAdded source. Key claims: ...",
  "tree_node": {{
    "topic_path": ["ParentTopic1", "ParentTopic2"],
    "description": "Brief description of what this document is about",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "sections": [
      {{
        "heading": "§ Section Title",
        "lines": "start-end",
        "summary": "Brief summary of this section's content"
      }}
    ]
  }}
}}
"""

    print("  calling Claude API...")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = extract_text_from_content(response.content)
    try:
        data = parse_json_from_response(raw)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing API response: {e}")
        print("Raw response saved to /tmp/ingest_debug.txt")
        Path("/tmp/ingest_debug.txt").write_text(raw)
        sys.exit(1)

    # Write source page
    slug = data["slug"]
    write_file(WIKI_DIR / "sources" / f"{slug}.md", data["source_page"])

    # Write entity pages (merge with existing if present)
    for page in data.get("entity_pages", []):
        write_file(WIKI_DIR / page["path"], page["content"], merge=True)

    # Write concept pages (merge with existing if present)
    for page in data.get("concept_pages", []):
        write_file(WIKI_DIR / page["path"], page["content"], merge=True)

    # Update overview
    if data.get("overview_update"):
        write_file(OVERVIEW_FILE, data["overview_update"])

    # Update index
    update_index(data["index_entry"], slug=slug, section="Sources")

    # Append log
    append_log(data["log_entry"])

    # Report contradictions
    contradictions = data.get("contradictions", [])
    if contradictions:
        print("\n  ⚠️  Contradictions detected:")
        for c in contradictions:
            print(f"     - {c}")

    # Update tree index
    tree_node = data.get("tree_node")
    if tree_node:
        update_tree_index(tree_node, kb_path)

    # Record successful ingestion for idempotency
    mark_ingested(kb_path, source, source_hash, slug, data["title"])

    print(f"\nDone. Ingested: {data['title']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a source document")
    parser.add_argument("source", help="Path to source document")
    parser.add_argument("--kb", type=str, required=True, help="Knowledge base name")
    args = parser.parse_args()

    kb_path, wiki_dir, raw_dir, tree_file = resolve_kb_path(args.kb)
    ingest(args.source, kb_path, wiki_dir, raw_dir, tree_file)

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

sys.path.insert(0, str(Path(__file__).parent))
from utils import call_claude, check_and_split_file


REPO_ROOT = Path(__file__).parent.parent
SCHEMA_FILE = REPO_ROOT / "CLAUDE.md"
META_FILE = REPO_ROOT / "meta.json"

# Inline format guide for ingest (replaces CLAUDE.md to reduce prompt size)
INGEST_FORMAT = """
## Wiki Structure (paths relative to wiki/ directory)
- sources/<slug>.md: 源文档摘要页
- entities/<Name>.md: 实体页（人/公司/项目/产品）
- concepts/<Name>.md: 概念页（思想/框架/方法）

## Source Page Format (sources/<slug>.md)
---
title: "文档标题"
type: source
date: YYYY-MM-DD
source_file: raw/...
---
## Summary
2-4句摘要

## Key Claims
- 要点1
- 要点2

## Key Quotes
> "引用内容"

## Connections
- [[EntityName]] — 关系
- [[ConceptName]] — 关系

## Contradictions
- 与 [[OtherPage]] 矛盾：原因

## Tree Node Format
{
  "topic_path": ["ParentTopic", "ChildTopic"],
  "description": "节点描述",
  "keywords": ["keyword1", "keyword2"],
  "sections": [{"heading": "§标题", "lines": "1-50", "summary": "章节摘要"}]
}
"""


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
        try:
            return json.loads(manifest_file.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_manifest(kb_path: Path, manifest: dict):
    """Save the ingest manifest."""
    manifest_file = kb_path / "wiki" / ".ingest-manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))


def _find_main_md(folder: Path) -> Path | None:
    """Find the main .md file in a folder. Prefers index.md, otherwise first .md found."""
    md_files = list(folder.glob("*.md"))
    if not md_files:
        return None
    # Prefer index.md
    for f in md_files:
        if f.name.lower() == "index.md":
            return f
    return md_files[0]


def _copy_dir(src: Path, dst: Path):
    """Recursively copy a directory, preserving structure."""
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        if item.is_file():
            rel = item.relative_to(src)
            dest_file = dst / rel
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_file)


def _build_content_with_images(source: Path, content: str, is_dir: bool) -> str:
    """Return content as-is. Claude's Read tool handles images natively via --add-dir."""
    return content


def merge_ingest_results(results: list[dict]) -> dict:
    """Merge results from processing multiple sections of a large file.

    Later results override earlier ones for title/slug, but entity_pages,
    concept_pages, contradictions, and sections are combined.
    """
    if not results:
        return {}
    if len(results) == 1:
        return results[0]

    merged = {
        "title": results[0].get("title", ""),
        "slug": results[0].get("slug", ""),
        "source_page": results[0].get("source_page", ""),
        "index_entry": results[0].get("index_entry", ""),
        "overview_update": results[-1].get("overview_update"),
        "entity_pages": [],
        "concept_pages": [],
        "contradictions": [],
        "log_entry": "",
        "tree_node": None,
    }

    all_sections = []

    for r in results:
        # Combine entity pages (deduplicate by path)
        seen_entity_paths = set(p["path"] for p in merged["entity_pages"])
        for ep in r.get("entity_pages", []):
            if ep["path"] not in seen_entity_paths:
                merged["entity_pages"].append(ep)
                seen_entity_paths.add(ep["path"])

        # Combine concept pages (deduplicate by path)
        seen_concept_paths = set(p["path"] for p in merged["concept_pages"])
        for cp in r.get("concept_pages", []):
            if cp["path"] not in seen_concept_paths:
                merged["concept_pages"].append(cp)
                seen_concept_paths.add(cp["path"])

        # Combine contradictions
        merged["contradictions"].extend(r.get("contradictions", []))

        # Collect tree sections
        tn = r.get("tree_node")
        if tn and tn.get("sections"):
            all_sections.extend(tn["sections"])

    # Build merged source_page from all results
    summaries = []
    for r in results:
        # Extract summary section from source_page if present
        sp = r.get("source_page", "")
        m = re.search(r"## Summary\n([\s\S]+?)(?=\n## |$)", sp)
        if m:
            summaries.append(m.group(1).strip())
        else:
            summaries.append(sp[:200])

    # Combine log entries
    log_entries = [r.get("log_entry", "") for r in results if r.get("log_entry")]
    merged["log_entry"] = " / ".join(log_entries)

    # Build merged tree_node
    if results[0].get("tree_node"):
        first_tn = results[0]["tree_node"]
        merged["tree_node"] = {
            "topic_path": first_tn.get("topic_path", []),
            "description": first_tn.get("description", ""),
            "keywords": first_tn.get("keywords", []),
            "sections": all_sections,
        }

    # Rebuild source_page with combined summary
    if summaries:
        merged["source_page"] = _rebuild_source_page(results[0], summaries)

    return merged


def _rebuild_source_page(first_result: dict, summaries: list[str]) -> str:
    """Rebuild source_page markdown with combined summaries from all sections."""
    sp = first_result.get("source_page", "")

    # Find and replace the Summary section
    combined = "\n\n".join(f"- {s}" for s in summaries if s.strip())

    if "## Summary" in sp:
        # Replace existing Summary section
        new_sp = re.sub(
            r"## Summary\n[\s\S]*?(?=\n## |$)",
            f"## Summary\n{combined}",
            sp
        )
        return new_sp
    else:
        # Prepend summary after frontmatter
        lines = sp.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("---"):
                insert_idx = i + 1
            elif insert_idx > 0 and line.strip() == "":
                break
        lines.insert(insert_idx, f"\n## Summary\n{combined}\n")
        return "\n".join(lines)


def mark_ingested(kb_path: Path, manifest_key: str, source_hash: str, slug: str, title: str):
    """Record this source as successfully ingested."""
    manifest = get_manifest(kb_path)
    manifest[manifest_key] = {
        "hash": source_hash,
        "slug": slug,
        "title": title,
    }
    save_manifest(kb_path, manifest)


def build_wiki_context() -> str:
    parts = []
    if INDEX_FILE.exists():
        parts.append(f"## wiki/index.md\n{read_file(INDEX_FILE)}")
    if OVERVIEW_FILE.exists():
        parts.append(f"## wiki/overview.md\n{read_file(OVERVIEW_FILE)}")
    # Include recent source pages for contradiction checking (reduced from 5 to 2)
    sources_dir = WIKI_DIR / "sources"
    if sources_dir.exists():
        recent = sorted(sources_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:2]
        for p in recent:
            parts.append(f"## {p.relative_to(REPO_ROOT)}\n{p.read_text()}")
    return "\n\n---\n\n".join(parts)


def update_tree_index(tree_node: dict, kb_path: Path, raw_path: str | None = None):
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
    if raw_path is None:
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

    today = date.today().isoformat()

    # --- Determine if source is a file or directory ---
    source_is_dir = source.is_dir()
    if source_is_dir:
        # Directory: copy entire tree, find main .md file
        main_md = _find_main_md(source)
        if not main_md:
            print(f"Error: no .md file found in directory: {source_path}")
            sys.exit(1)
        source_content = main_md.read_text(encoding="utf-8")
        source_hash = sha256(source_content)
        # Use folder name as manifest key
        manifest_key = source.name
        slug = source.name
        display_name = f"{source.name}/ (folder)"
        # Actual raw path is raw/{folder_name}/index.md
        main_md_rel = f"raw/{source.name}/{main_md.name}"
    else:
        # Single file
        main_md = source
        source_content = source.read_text(encoding="utf-8")
        source_hash = sha256(source_content)
        manifest_key = source.name
        slug = source.stem
        display_name = source.name
        main_md_rel = f"raw/{source.name}"

    # Idempotency check — skip if this exact source was already ingested
    manifest = get_manifest(kb_path)
    entry = manifest.get(manifest_key)
    if entry is not None and entry.get("hash") == source_hash:
        print(f"\nSkipping: {display_name}  (hash: {source_hash})")
        print(f"  Already ingested as '{entry['slug']}' — source unchanged.")
        return

    # Copy source to raw/ — file or directory
    if source.is_dir():
        # Copy entire directory structure
        dest_in_raw = raw_dir / source.name
        _copy_dir(source, dest_in_raw)
        print(f"  copied folder to: knowledge_bases/{kb_path.name}/raw/{source.name}/")
    else:
        dest_in_raw = raw_dir / source.name
        if not dest_in_raw.exists() or dest_in_raw.read_text() != source.read_text():
            raw_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest_in_raw)
            print(f"  copied to: {dest_in_raw.relative_to(REPO_ROOT)}")

    print(f"\nIngesting: {display_name}  (hash: {source_hash})")

    # --- Build content with embedded images ---
    content_to_ingest = _build_content_with_images(source, source_content, source_is_dir)

    wiki_context = build_wiki_context()

    INGEST_SCHEMA = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "slug": {"type": "string"},
            "source_page": {"type": "string"},
            "index_entry": {"type": "string"},
            "overview_update": {"type": ["string", "null"]},
            "entity_pages": {
                "type": "array",
                "items": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}}
            },
            "concept_pages": {
                "type": "array",
                "items": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}}
            },
            "contradictions": {"type": "array", "items": {"type": "string"}},
            "log_entry": {"type": "string"},
            "tree_node": {
                "type": "object",
                "properties": {
                    "topic_path": {"type": "array", "items": {"type": "string"}},
                    "description": {"type": "string"},
                    "keywords": {"type": "array", "items": {"type": "string"}},
                    "sections": {
                        "type": "array",
                        "items": {"type": "object", "properties": {"heading": {"type": "string"}, "lines": {"type": "string"}, "summary": {"type": "string"}}}
                    }
                }
            }
        },
        "required": ["title", "slug", "source_page", "index_entry", "entity_pages", "concept_pages", "contradictions", "log_entry", "tree_node"]
    }

    prompt = f"""You are maintaining an LLM Wiki. Process this source document and integrate its knowledge into the wiki.

## Wiki Format
{INGEST_FORMAT}

Current wiki state (index + recent pages):
{wiki_context if wiki_context else "(wiki is empty — this is the first source)"}

New source to ingest (file: {source.relative_to(REPO_ROOT) if source.is_relative_to(REPO_ROOT) else source.name}):
=== SOURCE START ===
{content_to_ingest}
=== SOURCE END ===

If the source contains image references (e.g. ![fig](path/to/image.png)), use the Read tool to view those images — Claude's Read tool handles images natively. The images are in the same directory tree you can access via --add-dir .

Today's date: {today}

Return JSON with: title, slug, source_page, index_entry, overview_update, entity_pages, concept_pages, contradictions, log_entry, tree_node.
"""

    # --- Check if file needs splitting ---
    _, split_sections = check_and_split_file(source if source.is_file() else main_md)

    if split_sections:
        # Process each section separately and merge results
        print(f"  processing {len(split_sections)} sections...")
        results = []
        for i, sec in enumerate(split_sections, 1):
            sec_prompt = f"""You are maintaining an LLM Wiki. Process this PART of a source document and integrate its knowledge into the wiki.

This is PART {i} of {len(split_sections)} from this document.
The document's title is the overall title (use from first part for title/slug).

## Wiki Format
{INGEST_FORMAT}

Current wiki state (index + recent pages):
{wiki_context if wiki_context else "(wiki is empty — this is the first source)"}

Source section (PART {i} of {len(split_sections)}):
=== SECTION START ===
Heading: {sec['heading'] or '(Document beginning)'}
Level: {sec['level']}
Content:
{sec['content'][:3000]}
=== SECTION END ===

If this section contains image references (e.g. ![fig](path/to/image.png)), use the Read tool to view those images — Claude's Read tool handles images natively.

Today's date: {today}

Return JSON with: title, slug, source_page, index_entry, overview_update, entity_pages, concept_pages, contradictions, log_entry, tree_node.
"""
            try:
                result = call_claude(sec_prompt, INGEST_SCHEMA, kb_path.name)
                results.append(result)
            except RuntimeError as e:
                print(f"  warning: failed to process section {i}: {e}")
                continue

        if not results:
            print(f"Error: no sections were successfully processed")
            sys.exit(1)

        # Merge results from all sections
        data = merge_ingest_results(results)
        print(f"  merged results from {len(results)} sections")
    else:
        # Normal single-pass processing
        print("  calling Claude...")
        try:
            data = call_claude(prompt, INGEST_SCHEMA, kb_path.name)
        except RuntimeError as e:
            print(f"Error: {e}")
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
        # For folder ingestion, pass the correct raw_path (not derived from slug)
        actual_raw_path = main_md_rel if source_is_dir else None
        update_tree_index(tree_node, kb_path, raw_path=actual_raw_path)

    # Record successful ingestion for idempotency
    mark_ingested(kb_path, manifest_key, source_hash, slug, data["title"])

    print(f"\nDone. Ingested: {data['title']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a source document")
    parser.add_argument("source", help="Path to source document")
    parser.add_argument("--kb", type=str, required=True, help="Knowledge base name")
    args = parser.parse_args()

    kb_path, wiki_dir, raw_dir, tree_file = resolve_kb_path(args.kb)
    ingest(args.source, kb_path, wiki_dir, raw_dir, tree_file)

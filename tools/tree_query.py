#!/usr/bin/env python3
"""
Query the LLM Tree Index for precise, line-level cited answers.

Usage:
    python tools/tree_query.py "<question>" --kb <name> [--save [path]]

The tree query searches the hierarchical tree index for relevant source documents,
retrieves exact line ranges, and synthesizes an answer with precise citations.

Flags:
    --kb <name>         Knowledge base name (required)
    --save [path]       Save answer to wiki (prompts for filename if path omitted)
"""

import sys
import json
import re
import argparse
from pathlib import Path
from datetime import date

from utils import call_claude_text, read_json

REPO_ROOT = Path(__file__).parent.parent
SCHEMA_FILE = REPO_ROOT / "CLAUDE.md"
META_FILE = REPO_ROOT / "meta.json"


def resolve_kb_path(kb_name: str | None) -> tuple[Path, Path, Path]:
    """Resolve knowledge base path. Returns (kb_path, wiki_dir, tree_file)."""
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
    tree_file = kb_path / "tree" / "index.json"
    return kb_path, wiki_dir, tree_file


WIKI_DIR = None
INDEX_FILE = None
LOG_FILE = None
KB_PATH = None


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  saved: {path.relative_to(REPO_ROOT)}")


def find_relevant_leaves(tree_data: dict, query: str, kb_path: Path) -> list[dict]:
    """DFS traverse tree, returning matching leaf nodes with relevance scores."""
    import string
    query_clean = query.translate(str.maketrans("", "", string.punctuation))
    query_words = set(w for w in query_clean.lower().split() if len(w) > 2)
    query_lower = query_clean.lower()
    results = []

    def text_match(text: str) -> tuple[bool, int]:
        """Check if query words match text. Returns (matched, score)."""
        text_lower = text.lower()
        score = 0
        matched = False
        for word in query_words:
            # Word boundary match
            if word in text_lower.split():
                score += 2
                matched = True
            # Substring match (for Chinese/CJK text, partial matches)
            if word in text_lower:
                score += 1
                matched = True
        return matched, score

    def score_node(node: dict) -> int:
        name = node.get("name", "")
        desc = node.get("description", "")
        keywords = node.get("keywords", [])
        sections = node.get("sections", [])

        score = 0
        # Name match
        matched, s = text_match(name)
        if matched:
            score += s
        # Description match
        matched, s = text_match(desc)
        if matched:
            score += s
        # Keyword match
        for kw in keywords:
            matched, s = text_match(kw)
            if matched:
                score += s
        # Section summaries
        for sec in sections:
            summary = sec.get("summary", "")
            heading = sec.get("heading", "")
            matched, s = text_match(summary)
            if matched:
                score += s
            matched, s = text_match(heading)
            if matched:
                score += s
        return score

    def traverse(node: dict):
        # Always traverse all children regardless of parent match
        if node.get("type") == "leaf":
            s = score_node(node)
            if s > 0:
                name = node.get("name", "")
                if name:
                    source_path = kb_path / name
                    # Security: ensure path stays within kb_path (prevent path traversal)
                    try:
                        source_path = source_path.resolve()
                        kb_path_resolved = kb_path.resolve()
                        if source_path.exists() and source_path.is_file() and \
                           source_path.relative_to(kb_path_resolved):
                            results.append({"node": node, "score": s})
                    except (ValueError, OSError):
                        pass
        for child in node.get("children", []):
            traverse(child)

    traverse(tree_data)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10]


def read_fragment(source_path: Path, lines: str) -> str:
    """Read a specific line range from a file. lines format: 'start-end' or 'start'."""
    try:
        if '-' in lines:
            start_str, end_str = lines.split('-', 1)
            start = int(start_str.strip())
            end = int(end_str.strip())
        else:
            start = int(lines.strip())
            end = start
        if start <= 0 or end <= 0 or start > end:
            return ""
    except (ValueError, OverflowError):
        return ""

    try:
        content = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""

    file_lines = content.split('\n')
    # Clamp end to file length
    end = min(end, len(file_lines))
    if start > len(file_lines):
        return ""
    return '\n'.join(file_lines[start - 1:end])


def append_log(entry: str):
    existing = read_file(LOG_FILE)
    LOG_FILE.write_text(entry.strip() + "\n\n" + existing)


def tree_query(question: str, kb_path: Path, wiki_dir: Path, tree_file: Path, save_path: str | None = None):
    global WIKI_DIR, INDEX_FILE, LOG_FILE, KB_PATH
    KB_PATH = kb_path
    WIKI_DIR = wiki_dir
    INDEX_FILE = wiki_dir / "index.md"
    LOG_FILE = wiki_dir / "log.md"

    today = date.today().isoformat()

    # Step 1: Load tree index
    if not tree_file.exists():
        print("Tree index is empty. Ingest some sources first with: python tools/ingest.py <source>")
        sys.exit(1)

    tree_data = read_json(tree_file, {"name": "root", "children": []})

    # Step 2: Find relevant leaves
    print(f"  searching tree index...")
    matches = find_relevant_leaves(tree_data, question, kb_path)

    if not matches:
        print("No relevant information found in the tree index.")
        print("Try ingesting relevant documents or rephrasing your query.")
        sys.exit(0)

    print(f"  found {len(matches)} relevant sections")

    # Step 3: Read fragments and build context
    sources_context = []
    citations = []

    for i, match in enumerate(matches, 1):
        node = match["node"]
        source_name = node.get("name", "")
        if not source_name:
            continue
        source_path = kb_path / source_name
        # Security: ensure path stays within kb_path
        try:
            source_path = source_path.resolve()
            kb_path_resolved = kb_path.resolve()
            source_path.relative_to(kb_path_resolved)
        except (ValueError, OSError):
            continue
        if not source_path.exists() or not source_path.is_file():
            continue

        sections = node.get("sections", [])
        source_content = read_file(source_path)

        for sec in sections:
            heading = sec.get("heading", "§")
            lines = sec.get("lines", "")
            summary = sec.get("summary", "")

            # Read the actual fragment
            if lines:
                fragment = read_fragment(source_path, lines)
                if fragment.strip():
                    sources_context.append(f"""
### Source {i}: {source_name}
Section: {heading} (lines {lines})
Content:
{fragment[:500]}
""")
                    citations.append({
                        "file": source_name,
                        "heading": heading,
                        "lines": lines,
                        "fragment": fragment[:300]
                    })

    if not sources_context:
        print("No readable source fragments found.")
        sys.exit(0)

    # Step 4: Synthesize answer via Claude
    print(f"  synthesizing answer...")
    context = "\n\n".join(sources_context)

    prompt = f"""You are querying a knowledge base tree index. Based on the source fragments below, answer the question with precise citations.

Question: {question}

Source fragments:
{context}

Write a well-structured answer. For each claim, cite the source using this format at the end of your answer:
来源：
[1] <file_path> § <heading> 行 <lines>
> "<quoted text>"

If multiple fragments support the same point, cite each one separately."""

    answer = call_claude_text(prompt, kb_path.name)

    # Build citation block
    citation_lines = ["\n来源："]
    for i, cit in enumerate(citations[:6], 1):  # max 6 citations
        citation_lines.append(f"[{i}] {cit['file']} § {cit['heading']} 行 {cit['lines']}")
        citation_lines.append(f"> \"{cit['fragment'][:150]}...\"")

    output = answer + "\n\n" + "\n".join(citation_lines)

    print("\n" + "=" * 60)
    print(output)
    print("=" * 60)

    # Step 5: Optionally save
    if save_path is not None:
        if save_path == "":
            slug = input("\nSave as (slug, e.g. 'my-analysis'): ").strip()
            if not slug:
                print("Skipping save.")
                return
            save_path = f"syntheses/{slug}.md"

        full_save_path = WIKI_DIR / save_path
        frontmatter = f"""---
title: "{question[:80]}"
type: synthesis
tags: []
sources: []
last_updated: {today}
---

"""
        write_file(full_save_path, frontmatter + output)

        # Update index
        index_content = read_file(INDEX_FILE)
        entry = f"- [{question[:60]}]({save_path}) — synthesis"
        if "## Syntheses" in index_content:
            index_content = index_content.replace("## Syntheses\n", f"## Syntheses\n{entry}\n")
            INDEX_FILE.write_text(index_content, encoding="utf-8")
        print(f"  indexed: {save_path}")

    append_log(f"## [{today}] tree_query | {question[:80]}\n\nTree query answered from {len(citations)} source sections." +
               (f" Saved to {save_path}." if save_path else ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the tree index")
    parser.add_argument("question", help="Question to ask the tree index")
    parser.add_argument("--kb", type=str, required=True, help="Knowledge base name")
    parser.add_argument("--save", nargs="?", const="", default=None,
                        help="Save answer to wiki (optionally specify path)")
    args = parser.parse_args()

    kb_path, wiki_dir, tree_file = resolve_kb_path(args.kb)
    tree_query(args.question, kb_path, wiki_dir, tree_file, args.save)

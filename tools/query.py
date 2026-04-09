#!/usr/bin/env python3
"""
Query the LLM Wiki.

Usage:
    python tools/query.py "What are the main themes?" --kb <name>
    python tools/query.py "How does ConceptA relate to ConceptB?" --kb <name> --save
    python tools/query.py "Summarize everything about EntityName" --kb <name> --save synthesis/my-analysis.md

Flags:
    --kb <name>         Knowledge base name (required)
    --save              Save the answer back into the wiki (prompts for filename)
    --save <path>       Save to a specific wiki path
"""

import sys
import re
import json
import os
import argparse
from pathlib import Path
from datetime import date

from utils import call_claude, call_claude_text

REPO_ROOT = Path(__file__).parent.parent
SCHEMA_FILE = REPO_ROOT / "CLAUDE.md"
META_FILE = REPO_ROOT / "meta.json"


def resolve_kb_path(kb_name: str | None) -> tuple[Path, Path, Path]:
    """解析知识库路径，返回 (kb_path, wiki_dir, index_file)"""
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
    return kb_path, wiki_dir, wiki_dir / "index.md"


WIKI_DIR = None  # set after parsing args
INDEX_FILE = None  # set after parsing args
LOG_FILE = None  # set after parsing args


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  saved: {path.relative_to(REPO_ROOT)}")


def find_relevant_pages(question: str, index_content: str) -> list[Path]:
    """Extract linked pages from index that seem relevant to the question."""
    # Pull all [[links]] and markdown links from index
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', index_content)
    # Simple keyword match: check if any word in the title appears in the question
    question_lower = question.lower()
    relevant = []
    for title, href in md_links:
        if any(word in question_lower for word in title.lower().split() if len(word) > 3):
            p = WIKI_DIR / href
            if p.exists():
                relevant.append(p)
    # Always include overview
    overview = WIKI_DIR / "overview.md"
    if overview.exists() and overview not in relevant:
        relevant.insert(0, overview)
    return relevant[:12]  # cap to avoid context overflow


def append_log(entry: str):
    existing = read_file(LOG_FILE)
    LOG_FILE.write_text(entry.strip() + "\n\n" + existing, encoding="utf-8")


def query(question: str, kb_path: Path, wiki_dir: Path, save_path: str | None = None):
    global WIKI_DIR, INDEX_FILE, LOG_FILE
    WIKI_DIR = wiki_dir
    INDEX_FILE = wiki_dir / "index.md"
    LOG_FILE = wiki_dir / "log.md"

    today = date.today().isoformat()
    client = None  # placeholder, no longer used

    # Step 1: Read index
    index_content = read_file(INDEX_FILE)
    if not index_content:
        print("Wiki is empty. Ingest some sources first with: python tools/ingest.py <source>")
        sys.exit(1)

    # Step 2: Find relevant pages
    relevant_pages = find_relevant_pages(question, index_content)

    # If no keyword match, ask Claude to identify relevant pages from the index
    if not relevant_pages or len(relevant_pages) <= 1:
        print("  selecting relevant pages via Claude...")
        selection_schema = {
            "type": "array",
            "items": {"type": "string"}
        }
        selection_prompt = f"""Given this wiki index:

{index_content}

Which pages are most relevant to answering: "{question}"

Return a JSON array of relative file paths (as listed in the index), e.g. ["sources/foo.md", "concepts/Bar.md"]. Maximum 10 pages."""

        try:
            paths = call_claude(selection_prompt, selection_schema, kb_path.name)
            if isinstance(paths, list):
                relevant_pages = [WIKI_DIR / p for p in paths if (WIKI_DIR / p).exists()]
        except (json.JSONDecodeError, TypeError):
            pass

    # Step 3: Read relevant pages
    pages_context = ""
    for p in relevant_pages:
        rel = p.relative_to(REPO_ROOT)
        pages_context += f"\n\n### {rel}\n{p.read_text(encoding='utf-8')}"

    if not pages_context:
        pages_context = f"\n\n### wiki/index.md\n{index_content}"

    schema = read_file(SCHEMA_FILE)

    # Step 4: Synthesize answer
    print(f"  synthesizing answer from {len(relevant_pages)} pages...")
    synthesis_prompt = f"""You are querying an LLM Wiki to answer a question. Use the wiki pages below to synthesize a thorough answer. Cite sources using [[PageName]] wikilink syntax.

Schema:
{schema}

Wiki pages:
{pages_context}

Question: {question}

Write a well-structured markdown answer with headers, bullets, and [[wikilink]] citations. At the end, add a ## Sources section listing the pages you drew from."""

    answer = call_claude_text(synthesis_prompt, kb_path.name)
    print("\n" + "=" * 60)
    print(answer)
    print("=" * 60)

    # Step 5: Optionally save answer
    if save_path is not None:
        if save_path == "":
            # Prompt for filename
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
        write_file(full_save_path, frontmatter + answer)

        # Update index
        index_content = read_file(INDEX_FILE)
        entry = f"- [{question[:60]}]({save_path}) — synthesis"
        if "## Syntheses" in index_content:
            index_content = index_content.replace("## Syntheses\n", f"## Syntheses\n{entry}\n")
            INDEX_FILE.write_text(index_content, encoding="utf-8")
        print(f"  indexed: {save_path}")

    # Append to log
    append_log(f"## [{today}] query | {question[:80]}\n\nSynthesized answer from {len(relevant_pages)} pages." +
               (f" Saved to {save_path}." if save_path else ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the LLM Wiki")
    parser.add_argument("question", help="Question to ask the wiki")
    parser.add_argument("--kb", type=str, required=True, help="Knowledge base name")
    parser.add_argument("--save", nargs="?", const="", default=None,
                        help="Save answer to wiki (optionally specify path)")
    args = parser.parse_args()

    kb_path, wiki_dir, _ = resolve_kb_path(args.kb)
    query(args.question, kb_path, wiki_dir, args.save)

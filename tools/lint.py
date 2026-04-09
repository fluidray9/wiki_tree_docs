#!/usr/bin/env python3
"""
Lint the LLM Wiki for health issues.

Usage:
    python tools/lint.py --kb <name>
    python tools/lint.py --kb <name> --save  # save lint report

Checks:
  - Orphan pages (no inbound wikilinks from other pages)
  - Broken wikilinks (pointing to pages that don't exist)
  - Missing entity pages (entities mentioned in 3+ pages but no page)
  - Contradictions between pages
  - Data gaps and suggested new sources
  - Tree structure issues (isolated topics, broken leaf references)
"""

import re
import sys
import os
import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import date

from utils import call_claude_text

REPO_ROOT = Path(__file__).parent.parent
SCHEMA_FILE = REPO_ROOT / "CLAUDE.md"
META_FILE = REPO_ROOT / "meta.json"


def resolve_kb_path(kb_name: str | None) -> tuple[Path, Path]:
    """解析知识库路径，返回 (kb_path, wiki_dir)"""
    if META_FILE.exists():
        meta = json.loads(META_FILE.read_text())
    else:
        meta = {"default": None}

    if kb_name is None:
        kb_name = meta.get("default")

    if not kb_name:
        print("Error: no knowledge base specified and no default set.")
        print("Use --kb <name> or run: python -m tools.tree-use <name>")
        sys.exit(1)

    kb_path = REPO_ROOT / "knowledge_bases" / kb_name
    if not kb_path.exists():
        print(f"Error: knowledge base not found: {kb_name}")
        sys.exit(1)

    wiki_dir = kb_path / "wiki"
    return kb_path, wiki_dir


WIKI_DIR = None  # set after parsing args
LOG_FILE = None  # set after parsing args
TREE_FILE = None  # set after parsing args


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def all_wiki_pages() -> list[Path]:
    return [p for p in WIKI_DIR.rglob("*.md")
            if p.name not in ("index.md", "log.md", "lint-report.md")]


def extract_wikilinks(content: str) -> list[str]:
    return re.findall(r'\[\[([^\]]+)\]\]', content)


def page_name_to_path(name: str) -> list[Path]:
    """Try to resolve a [[WikiLink]] to a file path."""
    candidates = []
    for p in all_wiki_pages():
        if p.stem.lower() == name.lower() or p.stem == name:
            candidates.append(p)
    return candidates


def find_orphans(pages: list[Path]) -> list[Path]:
    inbound = defaultdict(int)
    for p in pages:
        content = read_file(p)
        for link in extract_wikilinks(content):
            resolved = page_name_to_path(link)
            for r in resolved:
                inbound[r] += 1
    return [p for p in pages if inbound[p] == 0 and p != WIKI_DIR / "overview.md"]


def find_broken_links(pages: list[Path]) -> list[tuple[Path, str]]:
    broken = []
    for p in pages:
        content = read_file(p)
        for link in extract_wikilinks(content):
            if not page_name_to_path(link):
                broken.append((p, link))
    return broken


def find_missing_entities(pages: list[Path]) -> list[str]:
    """Find entity-like names mentioned in 3+ pages but lacking their own page."""
    mention_counts: dict[str, int] = defaultdict(int)
    existing_pages = {p.stem.lower() for p in pages}
    for p in pages:
        content = read_file(p)
        links = extract_wikilinks(content)
        for link in links:
            if link.lower() not in existing_pages:
                mention_counts[link] += 1
    return [name for name, count in mention_counts.items() if count >= 3]


def find_tree_issues(kb_path: Path) -> list[str]:
    """Check tree structure for issues."""
    issues = []
    tree_file = kb_path / "tree" / "index.json"

    if not tree_file.exists():
        issues.append("tree/index.json does not exist")
        return issues

    try:
        tree_data = json.loads(tree_file.read_text())
    except json.JSONDecodeError:
        issues.append("tree/index.json is not valid JSON")
        return issues

    raw_dir = kb_path / "raw"

    def check_node(node: dict, path: str = "root"):
        name = node.get("name", "?")
        node_type = node.get("type", "topic")
        children = node.get("children", [])

        if not isinstance(children, list):
            children = []

        if node_type == "leaf":
            # Check if source file exists (with path traversal protection)
            file_name = node.get("name", "")
            if file_name:
                source_path = kb_path / file_name
                try:
                    source_path_resolved = source_path.resolve()
                    kb_path_resolved = kb_path.resolve()
                    source_path_resolved.relative_to(kb_path_resolved)
                    if not source_path.exists():
                        issues.append(f"Leaf node references non-existent file: {file_name}")
                except (ValueError, OSError):
                    issues.append(f"Leaf node has invalid path: {file_name}")
        elif node_type == "topic":
            # Check for isolated topic nodes
            if not children and path != "root":
                issues.append(f"Orphan topic node: {name} (no children)")

        for child in children:
            check_node(child, f"{path}/{name}")

    if "children" in tree_data:
        for child in tree_data["children"]:
            check_node(child, "root")

    return issues


def run_lint(kb_path: Path, wiki_dir: Path):
    global WIKI_DIR, LOG_FILE, TREE_FILE
    WIKI_DIR = wiki_dir
    LOG_FILE = wiki_dir / "log.md"
    TREE_FILE = kb_path / "tree" / "index.json"

    pages = all_wiki_pages()
    today = date.today().isoformat()

    if not pages:
        print("Wiki is empty. Nothing to lint.")
        return ""

    print(f"Linting {len(pages)} wiki pages...")

    # Deterministic checks
    orphans = find_orphans(pages)
    broken = find_broken_links(pages)
    missing_entities = find_missing_entities(pages)
    tree_issues = find_tree_issues(kb_path)

    print(f"  orphans: {len(orphans)}")
    print(f"  broken links: {len(broken)}")
    print(f"  missing entity pages: {len(missing_entities)}")
    print(f"  tree issues: {len(tree_issues)}")

    # Build context for semantic checks (contradictions, gaps)
    # Use a sample of pages to stay within context limits
    sample = pages[:20]
    pages_context = ""
    for p in sample:
        rel = p.relative_to(REPO_ROOT)
        pages_context += f"\n\n### {rel}\n{read_file(p)[:1500]}"  # truncate long pages

    print("  running semantic lint via Claude CLI...")
    lint_prompt = f"""You are linting an LLM Wiki. Review the pages below and identify:
1. Contradictions between pages (claims that conflict)
2. Stale content (summaries that newer sources have superseded)
3. Data gaps (important questions the wiki can't answer — suggest specific sources to find)
4. Concepts mentioned but lacking depth

Wiki pages (sample of {len(sample)} pages):
{pages_context}

Return a markdown lint report with these sections:
## Contradictions
## Stale Content
## Data Gaps & Suggested Sources
## Concepts Needing More Depth

Be specific — name the exact pages and claims involved."""

    semantic_report = call_claude_text(lint_prompt, kb_path.name)

    # Compose full report
    report_lines = [
        f"# Wiki Lint Report — {today}",
        "",
        f"Scanned {len(pages)} pages.",
        "",
        "## Structural Issues",
        "",
    ]

    if orphans:
        report_lines.append("### Orphan Pages (no inbound links)")
        for p in orphans:
            report_lines.append(f"- `{p.relative_to(REPO_ROOT)}`")
        report_lines.append("")

    if broken:
        report_lines.append("### Broken Wikilinks")
        for page, link in broken:
            report_lines.append(f"- `{page.relative_to(REPO_ROOT)}` links to `[[{link}]]` — not found")
        report_lines.append("")

    if missing_entities:
        report_lines.append("### Missing Entity Pages (mentioned 3+ times but no page)")
        for name in missing_entities:
            report_lines.append(f"- `[[{name}]]`")
        report_lines.append("")

    if tree_issues:
        report_lines.append("### Tree Structure Issues")
        for issue in tree_issues:
            report_lines.append(f"- {issue}")
        report_lines.append("")

    if not orphans and not broken and not missing_entities and not tree_issues:
        report_lines.append("No structural issues found.")
        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")
    report_lines.append(semantic_report)

    report = "\n".join(report_lines)
    print("\n" + report)
    return report


def append_log(entry: str):
    existing = read_file(LOG_FILE)
    LOG_FILE.write_text(entry.strip() + "\n\n" + existing, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lint the LLM Wiki")
    parser.add_argument("--save", action="store_true", help="Save lint report to wiki/lint-report.md")
    parser.add_argument("--kb", type=str, default=None, help="Knowledge base name")
    args = parser.parse_args()

    kb_path, wiki_dir = resolve_kb_path(args.kb)
    report = run_lint(kb_path, wiki_dir)

    if args.save and report:
        report_path = wiki_dir / "lint-report.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"\nSaved: {report_path.relative_to(REPO_ROOT)}")

    today = date.today().isoformat()
    append_log(f"## [{today}] lint | Wiki health check\n\nRan lint. See lint-report.md for details.")

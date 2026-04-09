#!/usr/bin/env python3
"""
Initialize a new knowledge base.

Usage:
    python tools/init.py <name> [--alias "Alias Name"]

Examples:
    python tools/init.py ai_research
    python tools/init.py web_dev --alias "Web Development"
"""

import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
META_FILE = REPO_ROOT / "meta.json"


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  created: {path.relative_to(REPO_ROOT)}")


def init_kb(name: str, alias: str = ""):
    kb_path = REPO_ROOT / "knowledge_bases" / name

    if kb_path.exists():
        print(f"Error: knowledge base already exists: {name}")
        return

    print(f"Creating knowledge base: {name}")

    # Create directory structure
    (kb_path / "raw").mkdir(parents=True)
    print(f"  created: knowledge_bases/{name}/raw/")

    (kb_path / "wiki" / "sources").mkdir(parents=True)
    (kb_path / "wiki" / "entities").mkdir(parents=True)
    (kb_path / "wiki" / "concepts").mkdir(parents=True)
    (kb_path / "wiki" / "syntheses").mkdir(parents=True)
    (kb_path / "tree").mkdir(parents=True)
    print(f"  created: knowledge_bases/{name}/wiki/ & tree/ directories")

    # Write initial wiki files
    write_file(kb_path / "wiki" / "index.md",
        "# Wiki Index\n\n## Overview\n- [Overview](overview.md) — living synthesis\n\n## Sources\n\n## Entities\n\n## Concepts\n\n## Syntheses\n")

    write_file(kb_path / "wiki" / "overview.md",
        f"# Overview\n\nKnowledge base: {name}\n\n*(This overview will be updated as you ingest more sources.)*\n")

    write_file(kb_path / "wiki" / "log.md",
        f"## Initialized\n\nKnowledge base `{name}` created.\n")

    # Write initial tree index
    write_file(kb_path / "tree" / "index.json",
        json.dumps({
            "name": "root",
            "description": f"Knowledge base: {name}",
            "children": []
        }, indent=2, ensure_ascii=False))

    # Update meta.json
    meta = {}
    if META_FILE.exists():
        meta = json.loads(read_file(META_FILE))

    alias_map = meta.get("alias_map", {})
    alias_map[name] = alias
    meta["alias_map"] = alias_map

    # Set as default if no default exists
    if not meta.get("default"):
        meta["default"] = name

    write_file(META_FILE, json.dumps(meta, indent=2, ensure_ascii=False))

    default_note = ""
    if meta["default"] == name:
        default_note = " (set as default)"

    print(f"\nDone. Created knowledge base `{name}`{default_note}.")
    if alias:
        print(f"  Alias: {alias}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a new knowledge base")
    parser.add_argument("name", help="Knowledge base name (kebab-case recommended)")
    parser.add_argument("--alias", type=str, default="", help="Human-readable alias")
    args = parser.parse_args()

    init_kb(args.name, args.alias)

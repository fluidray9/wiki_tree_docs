#!/usr/bin/env python3
"""
Set the default knowledge base.

Usage:
    python tools/use.py <name>
    python tools/use.py --show    # show current default

Examples:
    python tools/use.py ai_research
    python tools/use.py --show
"""

import sys
import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
META_FILE = REPO_ROOT / "meta.json"
KB_DIR = REPO_ROOT / "knowledge_bases"

sys.path.insert(0, str(Path(__file__).parent))
from utils import read_json


def get_alias_text(alias_entry) -> str:
    """Get alias string from alias_map entry, supporting both old and new format."""
    if isinstance(alias_entry, dict):
        return alias_entry.get("alias", "")
    return alias_entry if alias_entry else ""


def show_default():
    meta = read_json(META_FILE, {})
    if not meta:
        print("No knowledge bases.")
        return

    default = meta.get("default")
    alias_map = meta.get("alias_map", {})

    if default:
        alias = get_alias_text(alias_map.get(default))
        if alias:
            print(f"Default: {default} — {alias}")
        else:
            print(f"Default: {default}")
    else:
        print("No default set.")


def use_kb(name: str):
    meta = read_json(META_FILE, {})

    kb_path = KB_DIR / name
    if not kb_path.exists():
        print(f"Error: knowledge base not found: {name}")
        print("Run: python tools/list.py")
        return

    meta["default"] = name

    # Ensure alias_map exists and migrate old format if needed
    if "alias_map" not in meta:
        meta["alias_map"] = {}
    else:
        # Migrate old string entries to new object format
        alias_map = meta["alias_map"]
        for k, v in list(alias_map.items()):
            if isinstance(v, str):
                alias_map[k] = {"alias": v, "description": ""}

    META_FILE.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    alias = get_alias_text(meta["alias_map"].get(name))
    if alias:
        print(f"Default knowledge base set to: {name} — {alias}")
    else:
        print(f"Default knowledge base set to: {name}")


if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser(description="Set the default knowledge base")
    parser.add_argument("name", nargs="?", help="Knowledge base name")
    parser.add_argument("--show", action="store_true", help="Show current default")
    args = parser.parse_args()

    if args.show:
        show_default()
    elif args.name:
        use_kb(args.name)
    else:
        show_default()

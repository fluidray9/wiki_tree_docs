#!/usr/bin/env python3
"""
List all knowledge bases.

Usage:
    python tools/list.py
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import read_json

REPO_ROOT = Path(__file__).parent.parent
META_FILE = REPO_ROOT / "meta.json"
KB_DIR = REPO_ROOT / "knowledge_bases"


def list_kb():
    meta = read_json(META_FILE, {})
    if not meta:
        print("No knowledge bases found.")
        return

    alias_map = meta.get("alias_map", {})
    default = meta.get("default")

    kbs = []
    if KB_DIR.exists():
        for kb_path in sorted(KB_DIR.iterdir()):
            if kb_path.is_dir():
                name = kb_path.name
                alias = alias_map.get(name, "")
                kbs.append((name, alias))

    if not kbs:
        print("No knowledge bases found.")
        return

    print("Available Knowledge Bases:")
    for name, alias in kbs:
        marker = ""
        if name == default:
            marker = " (default)"
        # Support both old format (string) and new format (object), handle None
        if isinstance(alias, dict):
            alias_text = alias.get("alias", "") or ""
            desc = alias.get("description", "") or ""
        elif isinstance(alias, str):
            alias_text = alias
            desc = ""
        else:
            alias_text = ""
            desc = ""
        if alias_text:
            print(f"  - {name}{marker} — {alias_text}")
        else:
            print(f"  - {name}{marker}")
        if desc:
            print(f"    {desc[:100]}{'...' if len(desc) > 100 else ''}")

    if default:
        print(f"\nDefault: {default}")
    else:
        print("\nNo default set. Use --kb <name> or `/tree-use` to set one.")


if __name__ == "__main__":
    list_kb()

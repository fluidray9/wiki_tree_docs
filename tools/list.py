#!/usr/bin/env python3
"""
List all knowledge bases.

Usage:
    python tools/list.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
META_FILE = REPO_ROOT / "meta.json"
KB_DIR = REPO_ROOT / "knowledge_bases"


def list_kb():
    if not META_FILE.exists():
        print("No knowledge bases found.")
        return

    meta = json.loads(META_FILE.read_text())
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
        # Support both old format (string) and new format (object)
        if isinstance(alias, dict):
            alias_text = alias.get("alias", "")
            desc = alias.get("description", "")
        else:
            alias_text = alias
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

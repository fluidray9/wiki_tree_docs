#!/usr/bin/env python3
"""
Delete a knowledge base and clean up meta.json references.

Usage:
    python tools/delete.py <name>          # delete with confirmation
    python tools/delete.py <name> --force  # skip confirmation
"""

import sys
import json
import shutil
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
META_FILE = REPO_ROOT / "meta.json"


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_file(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


def resolve_kb_name(kb_name: str | None) -> str:
    if kb_name is not None:
        return kb_name
    if META_FILE.exists():
        meta = json.loads(META_FILE.read_text())
        kb_name = meta.get("default")
    if not kb_name:
        print("Error: no knowledge base specified and no default set.")
        print("Use --kb <name> or set a default with: python tools/use.py <name>")
        sys.exit(1)
    return kb_name


def delete_kb(name: str, force: bool = False):
    kb_path = REPO_ROOT / "knowledge_bases" / name

    if not kb_path.exists():
        print(f"Error: knowledge base not found: {name}")
        sys.exit(1)

    # Confirm unless --force
    if not force:
        confirmed = input(f"Delete knowledge base '{name}'? This will remove all raw, wiki, and tree data. [y/N] ").strip().lower()
        if confirmed != "y":
            print("Aborted.")
            return

    # Remove the directory
    shutil.rmtree(kb_path)
    print(f"  deleted: knowledge_bases/{name}/")

    # Update meta.json
    if META_FILE.exists():
        meta = json.loads(META_FILE.read_text())

        # Remove from alias_map
        if name in meta.get("alias_map", {}):
            del meta["alias_map"][name]

        # Fix default if it points to deleted KB
        if meta.get("default") == name:
            remaining = list(meta.get("alias_map", {}).keys())
            meta["default"] = remaining[0] if remaining else None

        write_file(META_FILE, json.dumps(meta, indent=2, ensure_ascii=False))
        print(f"  updated: meta.json")

        if meta.get("default") is None:
            print("  (no default knowledge base set — use: python tools/use.py <name>)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete a knowledge base")
    parser.add_argument("name", help="Knowledge base name to delete")
    parser.add_argument("--force", action="store_true", help="Skip confirmation")
    args = parser.parse_args()

    delete_kb(args.name, force=args.force)

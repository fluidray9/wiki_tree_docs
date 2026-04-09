#!/usr/bin/env python3
"""
Shared utilities for LLM Tree Agent scripts.
Provides Claude CLI subprocess wrapper for structured JSON output.
"""

import subprocess
import json as _json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def call_claude(prompt: str, output_schema: dict, kb_name: str | None = None) -> dict:
    """Call claude -p CLI for structured JSON output. Returns parsed JSON result.

    Args:
        prompt: The prompt to send to Claude
        output_schema: JSON schema for structured output
        kb_name: Optional knowledge base name (passed for context)

    Returns:
        Parsed JSON object from Claude's structured output

    Raises:
        RuntimeError: If the claude CLI fails or output cannot be parsed
    """
    schema_json = _json.dumps(output_schema)

    cmd = [
        "claude", "-p",
        "--dangerously-skip-permissions",
        "--bare",
        "--output-format", "json",
        f"--json-schema", schema_json,
        "--add-dir", ".",
        "--allowedTools", "Read",
        "--no-session-persistence",
        prompt
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO_ROOT)
    )

    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr}")

    try:
        output = _json.loads(result.stdout)
        structured = output.get("structured_output")
        if structured:
            return structured
        # Fallback: try parsing result field
        raw_result = output.get("result", "")
        # Strip markdown code fences
        raw_result = re.sub(r"^```(?:json)?\s*", "", raw_result.strip())
        raw_result = re.sub(r"\s*```$", "", raw_result)
        # Try to find and parse JSON array or object
        match = re.search(r'[\[\{][\s\S]*[\]\}]', raw_result)
        if match:
            return _json.loads(match.group())
        raise ValueError(f"No structured output in claude response: {raw_result[:200]}")
    except (_json.JSONDecodeError, ValueError) as e:
        raise RuntimeError(f"Failed to parse claude JSON output: {e}\nRaw: {result.stdout[:500]}")


def call_claude_text(prompt: str, kb_name: str | None = None) -> str:
    """Call claude -p CLI for plain text output (no structured JSON schema).

    Args:
        prompt: The prompt to send to Claude
        kb_name: Optional knowledge base name

    Returns:
        Raw text response from Claude
    """
    cmd = [
        "claude", "-p",
        "--dangerously-skip-permissions",
        "--bare",
        "--output-format", "text",
        "--add-dir", ".",
        "--allowedTools", "Read",
        "--no-session-persistence",
        prompt
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO_ROOT)
    )

    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr}")

    return result.stdout


def read_file(path: Path) -> str:
    """Read a text file, returning empty string if it doesn't exist."""
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path, default=None) -> dict | list | None:
    """Read and parse JSON file, returning default if file doesn't exist or is invalid."""
    if not path.exists():
        return default if default is not None else None
    try:
        return _json.loads(path.read_text(encoding="utf-8"))
    except (_json.JSONDecodeError, IOError):
        return default if default is not None else None


def write_file(path: Path, content: str):
    """Write content to a file, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

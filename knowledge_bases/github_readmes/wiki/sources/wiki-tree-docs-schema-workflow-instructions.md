---
title: "Wiki Tree Docs — Schema & Workflow Instructions"
type: source
tags: []
date: 2026-04-09
source_file: raw/wiki-tree-docs-schema-workflow-instructions.md
---

## Summary
Wiki Tree Docs is a multi-knowledge-base skill for AI coding agents. Each knowledge base is an isolated workspace under `knowledge_bases/<name>/` with its own raw/, wiki/, and tree/ directories. The wiki index provides structured cross-referenced markdown pages; the tree index provides a hierarchical JSON structure for navigable retrieval with section-level granularity. A `meta.json` at the repo root stores alias mapping and the current default knowledge base. The system works with any Anthropic API-compatible provider (official Anthropic, MiniMax, AWS Bedrock, Google Vertex AI) and requires no API key for Claude Code usage.

## Key Claims
- Each knowledge base has isolated raw/ (immutable source documents), wiki/ (managed index pages), and tree/ (hierarchical JSON) workspaces
- The system supports slash commands (`/tree-init`, `/tree-list`, `/tree-use`, `/tree-delete`, `/tree-ingest`, `/tree-query`, `/wiki-query`, `/tree-lint`, `/tree-graph`) and Python scripts in `tools/`
- API compatibility spans Anthropic, MiniMax, AWS Bedrock, and Google Vertex AI via environment variables `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL`
- The execution model tries Python scripts first, then falls back to manual steps described in `skills/*.md`
- Tree node classification: matching by keywords/description, prefer existing nodes, add new leaf under matching topic, create new topic if no match
- The directory layout defines a clear separation between knowledge bases, wiki structure (index, overview, log, sources, entities, concepts, syntheses), and tree structure (JSON index)

## Key Quotes
> "Each knowledge base has its own source documents, wiki index, and tree index. No API key or Python scripts needed — just open this repo in Claude Code." — Overview

## Connections
- [[Anthropic]] — Provider of Claude Code, the agent for which this skill is designed
- [[Claude Code]] — The target AI coding agent that reads and executes this skill natively
- [[AgenticCodingTool]] — The paradigm this skill enables: autonomous, goal-oriented coding assistance
- [[ExtensibleIDE]] — Related through Claude Code's plugin system and VS Code's extension API as extensibility mechanisms

## Contradictions
- None identified in this section

## Notes
This document defines the schema, workflows, and conventions for the Wiki Tree Docs multi-knowledge-base system. It serves as both documentation and the skill definition that Claude Code reads automatically. Section 0 of this part contains introductory placeholder content; subsequent parts will cover the full document body.

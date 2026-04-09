# LLM Tree Index Agent — Schema & Workflow Instructions

A multi-knowledge-base skill for AI coding agents. Each knowledge base has its own source documents, wiki index, and tree index. No API key or Python scripts needed — just open this repo in Claude Code.

## Key Concepts

- **Knowledge Base**: An isolated workspace under `knowledge_bases/<name>/` with its own raw/, wiki/, and tree/
- **Wiki Index**: Structured markdown pages with cross-references (inherits from wiki-agent)
- **Tree Index**: Hierarchical JSON structure for navigable retrieval with section-level granularity
- **meta.json**: Located at repo root, stores alias mapping and current default knowledge base

## API Compatibility

The skill works with any **Anthropic API-compatible provider**. Environment variables:

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_AUTH_TOKEN` | API key (required for tools/ scripts) |
| `ANTHROPIC_BASE_URL` | API endpoint (default: `https://api.anthropic.com`) |

Examples of compatible providers:
- Official Anthropic API
- MiniMax (e.g., `https://api.minimaxi.com/anthropic`)
- AWS Bedrock (Claude models)
- Google Vertex AI (Claude models)

For Claude Code usage, no API key is needed — the agent handles it natively.

## Slash Commands

| Command | What to say |
|---|---|
| `/tree-init` | `init my_kb --alias "My KB"` |
| `/tree-list` | `list all knowledge bases` |
| `/tree-use` | `use my_kb` |
| `/tree-ingest` | `ingest raw/my-article.md --kb my_kb` |
| `/tree-query` | `query the tree about: what are the main themes? --kb my_kb` |
| `/wiki-query` | `query the wiki about: how does X work? --kb my_kb` |
| `/tree-lint` | `lint the knowledge base --kb my_kb` |
| `/tree-graph` | `build the knowledge graph --kb my_kb` |

Or describe in plain English. Claude Code reads this file automatically.

## Execution Model

When executing slash commands or workflows:
1. **Try the Python script first** — scripts in `tools/` are the primary execution layer
2. **If the script fails** (API error, network issue, etc.) — fall back to the manual steps described in the corresponding `skills/*.md` file

Each skill file (in `skills/`) describes both the script command to run and the manual fallback process.

---

## Directory Layout

```
llm-tree-agent/
├── meta.json              # Alias map + default knowledge base
│                         # {"alias_map": {"my_kb": "My Knowledge Base"}, "default": "my_kb"}
├── knowledge_bases/       # Parent directory for all knowledge bases
│   ├── my_kb/             # A knowledge base
│   │   ├── raw/           # Immutable source documents — never modify these
│   │   ├── wiki/           # Wiki index (managed entirely by agent)
│   │   │   ├── index.md    # Catalog — update on every ingest
│   │   │   ├── log.md      # Append-only chronological record
│   │   │   ├── overview.md  # Living synthesis across all sources
│   │   │   ├── sources/    # One summary page per source document
│   │   │   ├── entities/   # People, companies, projects, products
│   │   │   ├── concepts/   # Ideas, frameworks, methods, theories
│   │   │   └── syntheses/  # Saved query answers
│   │   └── tree/           # Tree index
│   │       └── index.json  # Hierarchical index structure
│   └── another_kb/         # Another knowledge base
│       ├── raw/
│       ├── wiki/
│       └── tree/
└── skills/                 # Sub-skill definitions
    ├── ingest.md           # Ingest workflow (generates both wiki + tree)
    ├── wiki-retrieval.md   # Wiki query workflow
    └── tree-retrieval.md   # Tree query workflow
```

---

## Meta.json Format

```json
{
  "alias_map": {
    "ai_research": "AI研究",
    "web_dev": "前端开发"
  },
  "default": "ai_research"
}
```

- `alias_map`: Maps knowledge base folder names to human-readable aliases
- `default`: The currently selected default knowledge base name, or `null` if none set

---

## Knowledge Base Management

### `/tree-init <name>`

Creates a new knowledge base with the given folder name (must be English, kebab-case recommended).

Steps:
1. Create `knowledge_bases/<name>/`
2. Create `knowledge_bases/<name>/raw/`
3. Create `knowledge_bases/<name>/wiki/` with initial `index.md`, `overview.md`, `log.md`
4. Create `knowledge_bases/<name>/tree/index.json` with initial empty tree
5. Add entry to `meta.json`'s `alias_map` (key = name, value = "")
6. If no default is set, set this as the default

### `/tree-list`

Reads `meta.json` and lists all knowledge bases with their aliases.

Output format:
```
Available Knowledge Bases:
- ai_research (AI研究)
- web_dev (前端开发)
- my_kb (no alias)

Default: ai_research
```

### `/tree-use <name>`

Sets the default knowledge base in `meta.json`.

Steps:
1. Verify `knowledge_bases/<name>/` exists
2. Update `meta.json`'s `default` field to `<name>`

After this, commands can omit `--kb` and will use this default.

---

## Resolving Knowledge Base Name

Before any operation that needs a knowledge base:

1. If `--kb <name>` is provided → use `<name>`
2. Else if `meta.json`'s `default` is not null → use `default`
3. Else → fail with: "No knowledge base specified and no default set. Use --kb <name> to specify."

---

## Ingest Workflow

Triggered by: `/tree-ingest <file> --kb <name>` or "ingest <file> into <name>"

Steps (all within the knowledge base's directory):
1. Read the source document fully
2. Read `wiki/index.md` and `wiki/overview.md` for current wiki context
3. Read `tree/index.json` for current tree structure
4. **Generate wiki index**:
   - Write `wiki/sources/<slug>.md`
   - Update `wiki/index.md`
   - Update `wiki/overview.md`
   - Update/create entity pages in `wiki/entities/`
   - Update/create concept pages in `wiki/concepts/`
   - Flag contradictions
   - Append to `wiki/log.md`
5. **Generate tree index** (simultaneously, not sequentially):
   - Analyze document topics → classify into tree nodes
   - For each section, generate section info (heading, line range, summary)
   - Merge new nodes into `tree/index.json` (do NOT rebuild existing structure)
6. **If this is the first document**, the tree node may be a new top-level topic

### Tree Node Classification Logic

When classifying a new document into the tree:
1. Read `tree/index.json`
2. Identify the document's main topic and keywords
3. Traverse existing tree nodes, match by `keywords` or `description`
4. If a matching topic node exists → add document as a `leaf` under its `children`
5. If no match → create a new topic node (may become a new top-level node)
6. Prefer existing nodes over creating new ones; avoid excessive tree depth

### Source Page Format (wiki/sources/)

```markdown
---
title: "Source Title"
type: source
tags: []
date: YYYY-MM-DD
source_file: raw/...
---

## Summary
2–4 sentence summary.

## Key Claims
- Claim 1
- Claim 2

## Key Quotes
> "Quote here" — context

## Connections
- [[EntityName]] — how they relate
- [[ConceptName]] — how it connects

## Contradictions
- Contradicts [[OtherPage]] on: ...
```

### Tree index.json Node Format

Each node has:
- `name`: Node name (folder name for topics, file path for leaves)
- `description`: What this node represents
- `keywords`: For topic matching during query
- `type`: "topic" (has children) or "leaf" (source document)
- `children`: Array of child nodes (for topic nodes only)
- `sections`: Array of section info (for leaf nodes only)

```json
{
  "name": "root",
  "description": "Knowledge base root",
  "children": [
    {
      "name": "AI",
      "description": "Artificial intelligence",
      "keywords": ["artificial intelligence", "machine learning"],
      "type": "topic",
      "children": [
        {
          "name": "LLM",
          "description": "Large language models",
          "keywords": ["language model", "transformer", "GPT"],
          "type": "topic",
          "children": []
        }
      ]
    }
  ]
}
```

A leaf node:
```json
{
  "name": "raw/papers/rag-survey.md",
  "type": "leaf",
  "sections": [
    {
      "heading": "§ Overview",
      "lines": "45-120",
      "summary": "RAG基本原理：通过检索增强语言模型的生成能力..."
    }
  ]
}
```

---

## Tree Query Workflow

Triggered by: `/tree-query "<question>" --kb <name>` or "query the tree about..."

Steps:
1. Resolve knowledge base (fail if none specified and no default)
2. Read `tree/index.json`
3. Match query keywords against node `keywords` and `sections[].summary` using DFS
4. Identify relevant leaf nodes
5. Read source document fragments using `sections[].lines` for precise line ranges
6. Generate answer with inline citations in format:

```
回答：<answer text>

来源：
[1] <knowledge_base>/raw/<filename> § <heading> 行 <line_start>-<line_end>
> "<quoted text>"

[2] ...
```

---

## Wiki Query Workflow

Triggered by: `/wiki-query "<question>" --kb <name>` or "what does the wiki say about..."

Steps:
1. Resolve knowledge base (fail if none specified and no default)
2. Read `wiki/index.md` to identify relevant pages
3. Read those pages
4. Synthesize answer with citations as `[[PageName]]` wikilinks
5. Ask if answer should be filed to `wiki/syntheses/<slug>.md`

Output format:
```
回答：<answer text>

来源：
[1] <knowledge_base>/wiki/sources/<filename>
[2] <knowledge_base>/wiki/concepts/<ConceptName>.md
```

---

## Lint Workflow

Triggered by: `/tree-lint --kb <name>` or "lint the tree index"

Checks:
- **Orphan nodes**: Tree nodes with no children (for topic nodes) or unreachable leaves
- **Broken leaves**: Leaf nodes pointing to non-existent source files
- **Empty topics**: Topic nodes with no meaningful content
- **Missing summaries**: Sections without proper summaries

---

## Graph Workflow

Triggered by: `/tree-graph --kb <name>` or "build the tree graph"

For tree index, generates a hierarchical visualization. (Future: could use tools/build_graph.py pattern for tree structure)

---

## Naming Conventions

- Knowledge base folders: `kebab-case` (e.g., `ai-research`, `web-dev`)
- Source slugs: `kebab-case` matching source filename
- Entity pages: `TitleCase.md`
- Concept pages: `TitleCase.md`
- Tree node names: Topic nodes use `Title-Case`, leaf nodes use file paths

---

## Index Format (wiki/index.md)

```markdown
# Wiki Index — <knowledge_base_name>

## Overview
- [Overview](overview.md) — living synthesis

## Sources
- [Source Title](sources/slug.md) — one-line summary

## Entities
- [Entity Name](entities/EntityName.md) — one-line description

## Concepts
- [Concept Name](concepts/ConceptName.md) — one-line description

## Syntheses
- [Analysis Title](syntheses/slug.md) — what question it answers
```

---

## Log Format (wiki/log.md)

Each entry: `## [YYYY-MM-DD] <operation> | <title>`

Operations: `init`, `ingest`, `query`, `lint`, `graph`

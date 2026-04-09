# Ingest Sub-Skill

Ingest a source document into a knowledge base, generating both wiki index and tree index simultaneously.

## Trigger

When user says `/tree-ingest <path> --kb <name>` or "ingest <path> into <name>"

## Prerequisites

1. Verify `knowledge_bases/<name>/` exists (fail if not)
2. Verify source file at `<path>` exists (fail if not)
3. Read `meta.json` to confirm knowledge base is valid

## Workflow

### Step 1: Read Source Document

Use Read tool to read the full source document. Note the file path and name.

### Step 2: Read Current Context

- Read `knowledge_bases/<name>/wiki/index.md`
- Read `knowledge_bases/<name>/wiki/overview.md`
- Read `knowledge_bases/<name>/tree/index.json`

### Step 3: Generate Wiki Index

Create/update the following within `knowledge_bases/<name>/wiki/`:

#### Source Page (wiki/sources/<slug>.md)

```markdown
---
title: "<Document Title>"
type: source
tags: []
date: YYYY-MM-DD
source_file: <relative path from raw/>
---

## Summary
2-4 sentence summary of the document.

## Key Claims
- Claim 1
- Claim 2

## Key Quotes
> "Quote here" — context

## Connections
- [[EntityName]] — how they relate
- [[ConceptName]] — how it connects

## Contradictions
- Contradicts [[OtherPage]] on: ... (if any)
```

#### Entity Pages (wiki/entities/)

For each person, company, project, or product mentioned:
- Create `wiki/entities/<Name>.md` with type `entity`
- Link from source page via `[[EntityName]]`

#### Concept Pages (wiki/concepts/)

For each idea, framework, method, or theory:
- Create `wiki/concepts/<ConceptName>.md` with type `concept`
- Link from source page via `[[ConceptName]]`

#### Update Index (wiki/index.md)

Add entry under Sources section:
```
- [Title](sources/slug.md) — one-line summary
```

#### Update Overview (wiki/overview.md)

Revise to incorporate new information. If this is the first source, create the initial overview.

#### Log (wiki/log.md)

Append:
```
## [YYYY-MM-DD] ingest | <Title>
```

### Step 4: Generate Tree Index (Simultaneously)

The tree index is generated at the same time as wiki, not after.

#### Analyze Document Structure

1. Parse markdown sections (lines starting with `## `)
2. For each major section:
   - Extract heading text (remove `## ` prefix)
   - Determine line range (start line to line before next `## `)
   - Generate a 1-2 sentence summary of the section content
3. Identify the document's main topic and related keywords

#### Classify Into Tree

1. Compare document topics/keywords against existing tree nodes
2. If a matching topic node exists:
   - Add document as a `leaf` node under the matching topic's children
3. If no match:
   - Create a new topic node (may be top-level or under existing relevant parent)
   - Add document as a `leaf` under the new topic

#### Update tree/index.json

Merge new nodes into existing tree. Do NOT rebuild existing structure.

Leaf node format:
```json
{
  "name": "<relative path from knowledge_base root, e.g. raw/file.md>",
  "type": "leaf",
  "sections": [
    {
      "heading": "§ <Section Title>",
      "lines": "<start>-<end>",
      "summary": "<1-2 sentence summary>"
    }
  ]
}
```

Topic node format:
```json
{
  "name": "<TopicName>",
  "description": "<topic description>",
  "keywords": ["keyword1", "keyword2"],
  "type": "topic",
  "children": []
}
```

### Step 5: Verify and Report

After ingest completes:
- Confirm wiki/source page created
- Confirm tree nodes added
- Report any contradictions flagged
- Ask if user wants to add more documents

## Error Handling

- If source file doesn't exist: "Source file not found: <path>"
- If knowledge base doesn't exist: "Knowledge base not found: <name>. Use /tree-init <name> to create it first."
- If source already ingested (by filename): Update existing entries rather than creating duplicates

## Example

```
User: /tree-ingest raw/papers/rag-survey.md --kb ai_research

Agent:
1. Reads raw/papers/rag-survey.md
2. Creates wiki/sources/rag-survey.md
3. Extracts entities (e.g., Meta AI, Google) → wiki/entities/
4. Extracts concepts (e.g., RAG, RLHF) → wiki/concepts/
5. Updates wiki/index.md, wiki/overview.md, wiki/log.md
6. Analyzes document sections and topics
7. Adds leaf node to tree under AI/LLM/RAG/ (or creates RAG node)
8. Reports completion
```

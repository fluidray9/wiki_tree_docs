# Wiki Retrieval Sub-Skill

Query the wiki index for a knowledge base and generate a synthesized answer with document-level citations.

## Trigger

When user says `/wiki-query "<question>" --kb <name>` or "what does the wiki say about <topic>"

## Prerequisites

1. Resolve knowledge base name (fail if none specified and no default)
2. Verify `knowledge_bases/<name>/` exists
3. Read `meta.json` to confirm

## Workflow

### Step 1: Resolve Knowledge Base

1. If `--kb <name>` provided → use `<name>`
2. Else if `meta.json`'s `default` is not null → use `default`
3. Else → fail with: "No knowledge base specified and no default set. Use --kb <name> to specify."

### Step 2: Read Wiki Index

Read `knowledge_bases/<name>/wiki/index.md` to understand the current wiki structure.

### Step 3: Identify Relevant Pages

Based on the query:
1. Identify which sources, entities, or concepts are relevant
2. Read `wiki/overview.md` for cross-cutting themes
3. Read relevant source pages from `wiki/sources/`
4. Read relevant entity pages from `wiki/entities/`
5. Read relevant concept pages from `wiki/concepts/`

### Step 4: Synthesize Answer

1. Analyze all collected information
2. Generate a comprehensive answer that synthesizes across multiple sources
3. Use `[[PageName]]` wikilinks for inline citations
4. Focus on understanding rather than quoting

### Step 5: Output Format

```
回答：<synthesized answer text>

来源：
[1] knowledge_bases/<name>/wiki/sources/<filename>
[2] knowledge_bases/<name>/wiki/concepts/<ConceptName>.md
[3] knowledge_bases/<name>/wiki/entities/<EntityName>.md
```

Note: Wiki retrieval uses document-level citations only (no chapter, line number, or quote).

### Step 6: Optional Save

Ask the user: "Would you like to save this answer to `wiki/syntheses/<slug>.md`?"

If yes, write:
```markdown
---
title: "<Query>"
type: synthesis
date: YYYY-MM-DD
sources: [<source pages used>]
---

## Question
<original question>

## Answer
<synthesized answer>

## Sources
- [[SourceName]](sources/slug.md)
- [[ConceptName]](concepts/ConceptName.md)
```

## Error Handling

- If knowledge base doesn't exist: "Knowledge base not found: <name>"
- If wiki has no content: "This knowledge base has no content yet. Use /tree-ingest to add documents."
- If query can't be answered from wiki: "The wiki doesn't have information about this. Consider ingesting relevant sources."

## Example

```
User: /wiki-query "RAG 和微调有什么区别？" --kb ai_research

Agent:
1. Resolves to ai_research knowledge base
2. Reads wiki/index.md
3. Identifies relevant pages: wiki/sources/rag-survey.md, wiki/sources/fine-tuning.md, wiki/concepts/RAG.md
4. Reads those pages
5. Synthesizes answer comparing RAG and fine-tuning
6. Outputs answer with document citations
```

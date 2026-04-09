# Wiki Retrieval Skill

Query the wiki index for a knowledge base using the Python tool. Falls back to manual execution if the script fails.

## Trigger

When user says `/wiki-query "<question>" --kb <name>` or "what does the wiki say about <topic>"

## Workflow

### Step 1: Try Script First

Run the query script:

```bash
python tools/query.py "<question>" --kb <name> [--save [path]]
```

Examples:
```bash
python tools/query.py "What is RAG?" --kb ai_research
python tools/query.py "How does BERT work?" --kb ai_research --save
```

Flags:
- `--kb <name>`: Knowledge base name (required)
- `--save [path]`: Save answer to wiki (prompts for filename if path omitted)

If the script succeeds, it will:
- Find relevant wiki pages
- Synthesize an answer using Claude
- Output with `[[wikilink]]` citations
- Optionally save to `wiki/syntheses/`

Done.

### Step 2: Fallback — Manual Execution

If the script fails (API error, network issue, etc.), execute manually:

1. Resolve knowledge base name
2. Read `knowledge_bases/<name>/wiki/index.md`
3. Identify relevant pages (sources, entities, concepts)
4. Read `wiki/overview.md` for cross-cutting themes
5. Read relevant source/entity/concept pages
6. Synthesize answer using `[[PageName]]` wikilinks
7. Ask if answer should be saved to `wiki/syntheses/<slug>.md`

Output format:
```
回答：<synthesized answer>

来源：
[1] knowledge_bases/<name>/wiki/sources/<filename>
[2] knowledge_bases/<name>/wiki/concepts/<ConceptName>.md
```

Note: Wiki retrieval uses document-level citations only (no chapter/line number/quote).

## Error Handling

- Script fails → Try manual execution
- Knowledge base not found → Report error
- Wiki has no content → "This knowledge base has no content yet. Use /tree-ingest to add documents."
- Query can't be answered → "The wiki doesn't have information about this. Consider ingesting relevant sources."

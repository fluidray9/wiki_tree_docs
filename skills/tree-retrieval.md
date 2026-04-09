# Tree Retrieval Skill

Query the tree index for a knowledge base using the Python tool. Falls back to manual execution if the script fails.

## Trigger

When user says `/tree-query "<question>" --kb <name>` or "query the tree about <topic>"

## Workflow

### Step 1: Try Script First

Run the tree query script:

```bash
python tools/tree_query.py "<question>" --kb <name> [--save [path]]
```

Examples:
```bash
python tools/tree_query.py "What is RAG?" --kb ai_research
python tools/tree_query.py "How do transformers work?" --kb ai_research --save
```

Flags:
- `--kb <name>`: Knowledge base name (required)
- `--save [path]`: Save answer to wiki (prompts for filename if path omitted)

If the script succeeds, it will:
- Search the tree index for relevant leaf nodes (matching keywords, description, and section summaries)
- Read the corresponding line ranges from source files
- Synthesize an answer using Claude with precise line-level citations
- Output in format: `raw/<filepath> § <heading> 行 <start>-<end> > "<quoted text>"`
- Optionally save to `wiki/syntheses/`

Done.

### Step 2: Fallback — Manual Execution

If the script fails (API error, network issue, etc.), execute manually:

1. Resolve knowledge base name
2. Read `knowledge_bases/<name>/tree/index.json`
3. Match query keywords against node `keywords` and `sections[].summary` using DFS
4. Identify relevant leaf nodes
5. Read source document fragments using `sections[].lines` for precise line ranges
6. Generate answer with inline citations

Output format:
```
回答：<answer based on quoted fragments>

来源：
[1] knowledge_bases/<name>/raw/<filename> § <heading> 行 <start>-<end>
> "<quoted text>"

[2] ...
```

**Scoring for matching:**
- Exact keyword match in `keywords`: +3
- Keyword match in `description`: +2
- Query term in section `summary`: +2 per match

**Line range reading:**
- offset: start line number
- limit: end line number - start line number + 1

## Error Handling

- Script fails → Try manual execution
- Knowledge base doesn't exist → "Knowledge base not found: <name>"
- Tree index is empty → "This knowledge base has no tree index yet. Use /tree-ingest to add documents."
- No matching nodes found → "No relevant information found in the tree index. Try a different query or ingest relevant documents."
- Source file doesn't exist (orphan leaf) → Skip and report as warning

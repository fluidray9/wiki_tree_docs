# Ingest Skill

Ingest a source document into a knowledge base using the Python tool. Falls back to manual execution if the script fails.

## Trigger

When user says `/tree-ingest <path> --kb <name>` or "ingest <path> into <name>"

## Workflow

### Step 1: Try Script First

Run the ingest script:

```bash
python tools/ingest.py <source> --kb <name>
```

Example:
```bash
python tools/ingest.py raw/papers/rag-survey.md --kb ai_research
```

If the script succeeds, it will:
- Copy the source to `knowledge_bases/<name>/raw/`
- Create `wiki/sources/<slug>.md`
- Create/Update entity pages in `wiki/entities/`
- Create/Update concept pages in `wiki/concepts/`
- Update `wiki/index.md`, `wiki/overview.md`, `wiki/log.md`
- Update `tree/index.json` with new tree nodes

Report the result to the user. Done.

### Step 2: Fallback — Manual Execution

If the script fails (API error, network issue, etc.), execute manually:

1. Read `knowledge_bases/<name>/wiki/index.md`
2. Read `knowledge_bases/<name>/wiki/overview.md`
3. Read `knowledge_bases/<name>/tree/index.json`
4. Read the full source document

Generate wiki content:
- Write `wiki/sources/<slug>.md`
- Write entity pages to `wiki/entities/`
- Write concept pages to `wiki/concepts/`
- Update `wiki/index.md`
- Update `wiki/overview.md`
- Append to `wiki/log.md`

Generate tree index:
- Analyze document sections (heading, line range, summary)
- Classify into tree nodes (match by keywords or create new topic)
- Merge into `tree/index.json`

Report any contradictions detected.

## Arguments

- `<source>`: Path to the source document (can be relative to repo root or absolute)
- `--kb <name>`: Knowledge base name (required; if omitted and default is set, uses default)

## Error Handling

- Script fails → Try manual execution
- Source file not found → Report error
- Knowledge base not found → Report error
- API error → Fallback to manual

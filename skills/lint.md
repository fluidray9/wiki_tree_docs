# Lint Skill

Lint a knowledge base for structural health issues using the Python tool. Falls back to manual execution if the script fails.

## Trigger

When user says `/tree-lint --kb <name>` or "lint the knowledge base"

## Workflow

### Step 1: Try Script First

Run the lint script:

```bash
python tools/lint.py --kb <name> [--save]
```

Examples:
```bash
python tools/lint.py --kb ai_research
python tools/lint.py --kb ai_research --save
```

Flags:
- `--kb <name>`: Knowledge base name (required)
- `--save`: Save the lint report to `wiki/lint-report.md`

If the script succeeds, it will check for:
- **Orphan pages**: Wiki pages with no inbound wikilinks
- **Broken wikilinks**: Links pointing to pages that don't exist
- **Missing entity pages**: Entities mentioned 3+ times but lacking a page
- **Tree structure issues**: Orphan topic nodes or leaf nodes pointing to non-existent source files
- **Contradictions**: Semantic conflicts between pages (via Claude)
- **Data gaps**: Missing topics suggested by existing references

Report the results to the user. Done.

### Step 2: Fallback — Manual Execution

If the script fails (API error, network issue, etc.), execute manually:

Check each category:

**Structural checks:**
1. List all wiki pages: `knowledge_bases/<name>/wiki/**/*.md`
2. Extract all `[[wikilinks]]` from content
3. Find pages with no inbound links → orphan pages
4. Find wikilinks that resolve to no existing file → broken links
5. Find entity-like names mentioned 3+ times but no page → missing entities

**Tree checks:**
1. Read `knowledge_bases/<name>/tree/index.json`
2. Check for topic nodes with no children → orphan topics
3. Check leaf nodes where `name` path doesn't exist → broken leaves

**Semantic checks (if needed):**
1. Read a sample of wiki pages
2. Ask Claude to identify contradictions, stale content, and data gaps

Output a lint report in markdown format.

## Error Handling

- Script fails → Try manual execution
- Knowledge base doesn't exist → "Knowledge base not found: <name>"
- Wiki is empty → "Nothing to lint — the wiki is empty."

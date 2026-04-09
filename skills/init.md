# Init Skill

Initialize a new knowledge base using the Python tool.

## Trigger

When user says `/tree-init <name> --alias "Alias Name"` or "create a new knowledge base called <name>"

## Workflow

### Step 1: Try Script First

Run the init script:

```bash
python tools/init.py <name> [--alias "Alias Name"]
```

Examples:
```bash
python tools/init.py ai_research
python tools/init.py web_dev --alias "Web Development"
```

If the script succeeds, it will:
- Create `knowledge_bases/<name>/`
- Create `raw/`, `wiki/`, `tree/` subdirectories
- Create initial `wiki/index.md`, `wiki/overview.md`, `wiki/log.md`
- Create initial `tree/index.json`
- Register in `meta.json`

Done.

### Step 2: Fallback — Manual Execution

If the script fails, execute manually:

1. Create directory structure:
```
knowledge_bases/<name>/
  raw/
  wiki/
    sources/
    entities/
    concepts/
    syntheses/
  tree/
```

2. Create initial files:
- `wiki/index.md` — wiki catalog
- `wiki/overview.md` — empty overview
- `wiki/log.md` — initialized log entry
- `tree/index.json` — empty tree `{"name": "root", "children": []}`

3. Update `meta.json`:
```json
{
  "alias_map": { "<name>": {"alias": "<alias>", "description": ""} },
  "default": "<name>"
}
```

## Arguments

- `<name>`: Knowledge base folder name (kebab-case recommended, e.g. `ai_research`)
- `--alias`: Optional human-readable alias (e.g. `"AI Research"`)

## Error Handling

- KB already exists → Report error
- Name conflict in meta.json → Report error

# List Skill

List all knowledge bases and show which one is the default.

## Trigger

When user says `/tree-list` or "list all knowledge bases"

## Workflow

### Step 1: Try Script First

```bash
python tools/list.py
```

### Step 2: Manual Fallback

Read `meta.json` and `knowledge_bases/` directory directly:
- Parse `meta.json` → `alias_map` and `default`
- List subdirectories in `knowledge_bases/`
- Output each KB with its alias and whether it's the default

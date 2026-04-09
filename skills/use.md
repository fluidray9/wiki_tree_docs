# Use Skill

Set or show the default knowledge base.

## Trigger

When user says `/tree-use <name>` or "use <name> as the default knowledge base"

## Workflow

### Step 1: Try Script First

Show current default:
```bash
python tools/use.py --show
```

Set default:
```bash
python tools/use.py <name>
```

Examples:
```bash
python tools/use.py ai_research
python tools/use.py --show
```

If the script succeeds, it updates `meta.json` and confirms the new default.

### Step 2: Manual Fallback

1. Read existing `meta.json`
2. Verify `knowledge_bases/<name>/` exists
3. Update `meta.json`:
```json
{
  "default": "<name>"
}
```

## Arguments

- `<name>`: Knowledge base name to set as default
- `--show`: Just display the current default without changing it

## Error Handling

- KB doesn't exist → "Knowledge base not found: <name>"

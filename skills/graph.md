# Graph Skill

Build an interactive knowledge graph visualization using the Python tool. Falls back to manual execution if the script fails.

## Trigger

When user says `/tree-graph --kb <name>` or "build the knowledge graph"

## Workflow

### Step 1: Try Script First

Run the graph script:

```bash
python tools/build_graph.py --kb <name> [--open]
```

Examples:
```bash
python tools/build_graph.py --kb ai_research
python tools/build_graph.py --kb ai_research --open
```

Flags:
- `--kb <name>`: Knowledge base name (required)
- `--no-infer`: Skip semantic relationship inference (avoids extra API calls)
- `--open`: Open the generated graph.html in browser

If the script succeeds, it will:
- Pass 1: Extract all `[[wikilinks]]` from wiki pages → deterministic edges
- Pass 2: (Optional) Use Claude to infer implicit semantic relationships → inferred edges
- Run Louvain community detection for clustering
- Output: `knowledge_bases/<name>/graph/graph.json` and `graph.html`

Done.

### Step 2: Fallback — Manual Execution

If the script fails (API error, network issue, etc.), execute manually:

1. Read all wiki pages from `knowledge_bases/<name>/wiki/`
2. Extract all `[[wikilinks]]` → deterministic edges
3. Build a graph structure (nodes = pages, edges = wikilinks)
4. Use Claude to infer implicit relationships (optional)
5. Apply community detection (Louvain algorithm)
6. Generate graph.html with vis.js visualization

## Error Handling

- Script fails → Try manual execution
- Knowledge base doesn't exist → "Knowledge base not found: <name>"
- Wiki is empty → "Nothing to graph — the wiki is empty."
- API error during inference → Retry with `--no-infer` to skip semantic inference

# Tree Retrieval Skill

Query the tree index for a knowledge base to get precise line-level citations. **Note: No script available yet — uses manual execution only.**

## Trigger

When user says `/tree-query "<question>" --kb <name>` or "query the tree about <topic>"

## Workflow

### Step 1: Resolve Knowledge Base

1. If `--kb <name>` provided → use `<name>`
2. Else if `meta.json`'s `default` is not null → use `default`
3. Else → fail with: "No knowledge base specified and no default set. Use --kb <name> to specify."

### Step 2: Read Tree Index

Read `knowledge_bases/<name>/tree/index.json` to understand the tree structure.

### Step 3: Match Query to Tree Nodes

1. Parse query to extract keywords
2. DFS traverse the tree, matching against:
   - Node `keywords` array
   - Node `description`
   - Leaf node `sections[].summary` (most important for retrieval)
3. Collect all matching leaf nodes (source documents)
4. For each matching leaf, note the relevant sections

**Scoring:**
- Exact keyword match in `keywords`: +3
- Keyword match in `description`: +2
- Query term in section `summary`: +2 per match
- Multiple matches in same section: +1 bonus

### Step 4: Read Source Document Fragments

For each matching leaf node:
1. Construct the full path: `knowledge_bases/<name>/<leaf.name>`
2. Use the section's `lines` field to read only that portion
3. Extract the exact quoted text from that range

**Line range reading:**
- offset: start line number
- limit: end line number - start line number + 1

Example: To read lines 45-120:
- offset: 45
- limit: 76

### Step 5: Generate Answer with Citations

```
回答：<answer based on quoted fragments>

来源：
[1] knowledge_bases/<name>/raw/<filename> § <heading> 行 <start>-<end>
> "<quoted text>"

[2] ...
```

Format rules:
- Use `§ ` prefix for section heading (e.g., `§ Overview`, `§ 概述`)
- Line numbers from the `lines` field (e.g., `行 45-47`)
- Quote the exact text from the source
- If multiple quotes from same file, use separate numbered entries

### Step 6: Verification

Verify that the quoted text actually supports the answer claim. If not:
- Find additional relevant sections
- Qualify the answer with "Based on the sources..."

## Node Matching Logic

```
function findRelevantLeaves(query, node):
  if node.type == "leaf":
    score = matchScore(query, node.sections)
    return [(node, score)] if score > threshold
  else:
    results = []
    for child in node.children:
      results += findRelevantLeaves(query, child)
    return results sorted by score
```

## Error Handling

- Knowledge base doesn't exist → "Knowledge base not found: <name>"
- Tree index is empty → "This knowledge base has no tree index yet. Use /tree-ingest to add documents."
- No matching nodes found → "No relevant information found in the tree index. Try a different query or ingest relevant documents."
- Source file doesn't exist (orphan leaf) → Skip and report as warning

## Future

When `tools/tree_query.py` is created, update this skill to try the script first before manual execution.

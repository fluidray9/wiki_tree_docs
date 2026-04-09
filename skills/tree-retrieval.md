# Tree Retrieval Sub-Skill

Query the tree index for a knowledge base and generate an answer with precise原文引用 (file, section, line numbers, and quoted text).

## Trigger

When user says `/tree-query "<question>" --kb <name>` or "query the tree about <topic>"

## Prerequisites

1. Resolve knowledge base name (fail if none specified and no default)
2. Verify `knowledge_bases/<name>/` exists
3. Read `meta.json` to confirm

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

### Step 4: Read Source Document Fragments

For each matching leaf node:
1. Construct the full path: `knowledge_bases/<name>/<leaf.name>`
2. Use the section's `lines` field to read only that portion of the file
3. Extract the exact quoted text from that range

### Step 5: Generate Answer with Citations

```
回答：<answer based on quoted fragments>

来源：
[1] knowledge_bases/<name>/raw/<filename> § <heading> 行 <start>-<end>
> "<quoted text>"

[2] knowledge_bases/<name>/raw/<filename> § <heading> 行 <start>-<end>
> "<quoted text>"
```

Format rules:
- Use `§ ` prefix for section heading (e.g., `§ Overview`, `§ 概述`)
- Line numbers from the `lines` field (e.g., `行 45-47`)
- Quote the exact text from the source
- If multiple quotes from same file, use separate numbered entries

### Step 6: Verification

Verify that the quoted text actually supports the answer claim. If not, either:
- Find additional relevant sections
- Qualify the answer with "Based on the sources..."

## Node Matching Logic

### Matching Algorithm

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

### Scoring

- Exact keyword match in `keywords`: +3
- Keyword match in `description`: +2
- Query term in section `summary`: +2 per match
- Multiple matches in same section: +1 bonus

## Error Handling

- If knowledge base doesn't exist: "Knowledge base not found: <name>"
- If tree index is empty: "This knowledge base has no tree index yet. Use /tree-ingest to add documents."
- If no matching nodes found: "No relevant information found in the tree index. Try a different query or ingest relevant documents."
- If source file doesn't exist (orphan leaf): Skip and report as warning

## Example

```
User: /tree-query "RAG 的基本原理是什么？" --kb ai_research

Agent:
1. Resolves to ai_research knowledge base
2. Reads tree/index.json
3. Matches query against keywords and section summaries
   - Found: AI/LLM/RAG/raw/rag-survey.md (sections: Overview, Retrieval Methods)
   - Found: AI/LLM/RAG/raw/rag-intro.md (sections: 概述)
4. Reads rag-survey.md lines 45-120 for Overview section
5. Reads rag-intro.md lines 1-50 for 概述 section
6. Extracts relevant quotes
7. Generates answer with citations:
   回答：RAG 通过检索增强语言模型的生成能力...

   来源：
   [1] knowledge_bases/ai_research/raw/rag-survey.md § Overview 行 45-47
   > "Retrieval-augmented generation (RAG) is a technique..."

   [2] knowledge_bases/ai_research/raw/rag-intro.md § 概述 行 12-14
   > "RAG combines retrieval and generation..."
```

## Line Range Reading

When reading a specific line range from a file, use the Read tool with offset and limit parameters:
- `offset`: start line number
- `limit`: end line number - start line number + 1

Example: To read lines 45-120:
- `offset: 45`
- `limit: 76` (120 - 45 + 1)

Note: Line numbers in the tree index are 1-indexed, matching standard file line numbering.

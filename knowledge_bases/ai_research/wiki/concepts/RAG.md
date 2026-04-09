---
title: "RAG"
type: concept
tags: ["Retrieval-Augmented Generation", "知识检索", "RAG"]
sources: ["rag-intro"]
last_updated: 2026-04-09
---

## Definition
RAG（Retrieval-Augmented Generation，检索增强生成）是一种将信息检索与语言模型生成相结合的技术架构。

## Key Components
- **检索器（Retriever）**：从向量数据库中检索与查询相关的文档片段
- **生成器（Generator）**：基于检索结果和问题生成答案
- **增强器（Augmenter）**：将检索结果与原问题融合

## Related Sources
- [[rag-intro]]

## Connections
- [[问答系统]] — RAG 的应用场景
- [[向量数据库]] — RAG 检索的存储后端

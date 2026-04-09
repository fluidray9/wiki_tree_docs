---
title: "RAG"
type: concept
tags: ["RAG", "Retrieval-Augmented Generation", "知识检索", "LLM"]
date: 2026-04-09
---

## Definition
RAG（Retrieval-Augmented Generation，检索增强生成）是一种将信息检索与语言模型生成相结合的技术。它通过从外部知识库中检索相关信息，然后利用这些信息增强语言模型的生成能力。

## Core Components
1. **Retriever（检索器）**：从向量数据库中检索相关文档
2. **Generator（生成器）**：基于检索结果生成答案
3. **Augmenter（增强器）**：融合检索结果与原问题

## Key Characteristics
- 可解释性强：答案可追溯到源文档
- 实时性好：知识库可实时更新
- 避免幻觉：基于真实检索内容生成

## Applications
- 问答系统
- 文档摘要生成
- 对话系统
- 知识密集型任务

## Related Sources
- [[rag-intro]] — RAG 基础介绍
- [[rag-intro-v2]] — RAG 详解
- [[rag-detailed-principles]] — RAG 原理详解

## Related Concepts
- [[Transformer]] — 底层模型架构
- [[LLM]] — 大型语言模型

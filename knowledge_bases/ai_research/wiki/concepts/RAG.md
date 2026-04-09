---
title: "RAG"
type: concept
tags: ["RAG", "Retrieval-Augmented Generation", "LLM", "知识检索"]
date: 2026-04-09
---

## 定义
RAG（Retrieval-Augmented Generation，检索增强生成）是一种将信息检索与语言模型生成相结合的技术。它通过从外部知识库中检索相关信息，然后利用这些信息增强语言模型的生成能力。

## 核心组件
- **检索器（Retriever）**：从向量数据库中检索相关文档
- **生成器（Generator）**：基于检索结果生成答案
- **增强器（Augmenter）**：融合检索结果与原问题

## 应用场景
- 问答系统
- 文档摘要生成
- 对话系统

## 优缺点
**优点**：
- 可解释性强
- 实时性好
- 易于更新知识库

**缺点**：
- 依赖检索质量
- 延迟较高

## 相关文档
- [[RAG 介绍]]
- [[RAG 介绍 v2]]

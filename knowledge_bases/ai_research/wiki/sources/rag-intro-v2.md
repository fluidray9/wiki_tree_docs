---
title: "RAG 介绍"
type: source
tags: ["RAG", "Retrieval-Augmented Generation", "知识检索", "LLM"]
date: 2026-04-09
source_file: raw/rag-intro.md
---

## Summary
RAG（Retrieval-Augmented Generation）是一种将检索与生成结合的技术。它通过从外部知识库中检索相关信息，然后利用这些信息增强语言模型的生成能力。

## Key Claims
- RAG 系统由检索器、生成器、增强器三个组件构成
- 检索器从向量数据库中检索相关文档片段
- 生成器基于检索结果和问题生成答案
- RAG 广泛应用于问答系统、文档摘要生成、对话系统
- RAG 优点：可解释性强、实时性好、易于更新知识库
- RAG 缺点：依赖检索质量、延迟较高

## Key Quotes
> "RAG（Retrieval-Augmented Generation）是一种将检索与生成结合的技术。它通过从外部知识库中检索相关信息，然后利用这些信息增强语言模型的生成能力。" — 核心定义

## Connections
- [[RAG]] — 核心概念
- [[Retriever]] — 检索器组件
- [[Generator]] — 生成器组件
- [[Augmenter]] — 增强器组件

## Contradictions
- 与现有 sources/rag-intro.md 内容高度相似，可能是同一文档的不同版本或重复摄入。

## Notes
此文档与现有 rag-intro.md 内容和结构完全一致，建议确认是否为重复文档。

---
title: "RAG 介绍"
type: source
tags: ["RAG", "Retrieval-Augmented Generation", "知识检索", "LLM", "RAG原理"]
date: 2026-04-09
source_file: raw/rag-intro.md
---

## Summary
RAG（Retrieval-Augmented Generation）是一种将检索与生成结合的技术，通过从外部知识库中检索相关信息来增强语言模型的生成能力。系统由检索器、生成器、增强器三个核心组件构成，广泛应用于问答、摘要、对话等场景。

## Key Claims
- RAG 系统由检索器（Retriever）、生成器（Generator）和增强器（Augmenter）三个组件构成
- 检索器负责从向量数据库中找到与问题相关的文档片段
- 生成器基于检索片段和问题生成最终答案
- RAG 优势：可解释性强、实时性好、易于更新知识库
- RAG 优势：可动态利用外部知识，避免模型幻觉
- RAG 劣势：依赖检索质量、延迟较高

## Key Quotes
> "RAG（Retrieval-Augmented Generation）是一种将检索与生成结合的技术。它通过从外部知识库中检索相关信息，然后利用这些信息增强语言模型的生成能力。" — 核心定义

## Connections
- [[RAG]] — 核心概念
- [[Retriever]] — 检索器组件
- [[Generator]] — 生成器组件
- [[Augmenter]] — 增强器组件

## Contradictions
- 与现有 sources/rag-intro.md 和 sources/rag-intro-v2.md 内容高度相似，结构一致。此文档为同一来源的重复摄入或简化版本。

## Notes
此文档与现有 rag-intro.md 和 rag-intro-v2.md 的内容和结构完全一致，建议确认是否需要保留多个副本，或统一为一个标准文档。

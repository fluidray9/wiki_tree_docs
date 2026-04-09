---
title: "Generator"
type: entity
tags: ["RAG", "组件", "生成"]
date: 2026-04-09
---

## Overview
Generator（生成器）是 RAG 系统的核心组件之一，负责基于检索结果和原始问题生成最终答案。

## Details
- 接收检索到的文档片段和原始问题
- 将检索内容与问题融合输入语言模型
- 生成最终的自然语言回答
- 通常使用 GPT、LLaMA 等大语言模型作为生成器

## Connected Sources
- [[rag-intro]] — RAG 系统概述
- [[rag-intro-v2]] — RAG 技术详解
- [[rag-detailed-principles]] — RAG 原理详解

## Related Entities
- [[Retriever]] — 检索器组件
- [[Augmenter]] — 增强器组件
- [[RAG]] — 父级概念

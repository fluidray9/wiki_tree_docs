---
title: "Retriever"
type: entity
tags: ["RAG", "组件", "检索"]
date: 2026-04-09
---

## Overview
Retriever（检索器）是 RAG 系统的核心组件之一，负责从向量数据库中找到与用户问题相关的文档片段。

## Details
- 接收用户查询（问题）
- 将查询转换为向量表示
- 在向量数据库中进行相似度搜索
- 返回 Top-K 个最相关的文档片段

## Connected Sources
- [[rag-intro]] — RAG 系统概述
- [[rag-intro-v2]] — RAG 技术详解
- [[rag-detailed-principles]] — RAG 原理详解

## Related Entities
- [[Generator]] — 生成器组件
- [[Augmenter]] — 增强器组件
- [[RAG]] — 父级概念

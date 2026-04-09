---
title: "Multi-Head Attention"
type: concept
tags: ["Attention Mechanism", "Transformer"]
date: 2026-04-09
---

# Multi-Head Attention (多头注意力)

## 定义
多头注意力机制是 Transformer 的核心组件之一，并行计算多个注意力头，使模型能够关注不同位置的多种表示子空间。

## 工作原理
1. 将 Q、K、V 矩阵线性投影到 h 个不同的子空间
2. 并行计算 h 个独立的注意力
3. 拼接所有头的输出并再次线性投影

## 核心优势
- 捕获多种不同类型的关系
- 增强模型的表达能力
- 提供更丰富的表示

## 相关链接
- [[Transformer]] — 使用多头注意力的核心架构
- [[Self-Attention]] — 单头注意力机制

## 来源
- knowledge_bases/ai_research/wiki/sources/transformer-intro-v3.md

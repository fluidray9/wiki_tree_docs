---
title: "Self-Attention"
type: concept
tags: ["Attention Mechanism", "Deep Learning"]
date: 2026-04-09
---

## 定义
自注意力机制（Self-Attention）是 Transformer 架构的核心组件，通过计算序列内部元素之间的关联性来捕捉上下文依赖关系。

## 工作原理
1. 对输入序列的每个位置计算 Query、Key、Value 向量
2. 通过 Query 与所有 Key 的点积计算注意力分数
3. 应用 softmax 得到注意力权重
4. 用注意力权重对 Value 加权求和得到输出

## 优势
- 可捕捉任意距离的依赖关系（长距离依赖）
- 支持并行计算
- 增强模型对上下文语义的理解

## 相关概念
- [[Transformer]] — 使用自注意力的架构
- [[Multi-head Attention]] — 多头自注意力
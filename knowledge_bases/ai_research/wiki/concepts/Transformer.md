---
title: "Transformer"
type: concept
tags: ["Neural Network", "Deep Learning", "Attention Mechanism"]
date: 2026-04-09
---

## 定义
Transformer 是一种基于自注意力机制（Self-Attention）的神经网络架构，由 Vaswani 等人在 2017 年提出。它完全摒弃了传统的循环神经网络结构，采用注意力机制并行处理序列数据。

## 核心组件
1. **多头注意力机制（Multi-Head Attention）**：并行计算多个注意力头，捕捉不同类型的依赖关系
2. **前馈神经网络（FFNN）**：对每个位置独立进行处理
3. **位置编码（Positional Encoding）**：注入序列位置信息

## 关键特性
- 完全并行化处理，训练效率高
- 可捕捉长距离依赖关系
- 易于扩展和规模化

## 应用
- **NLP**: BERT、GPT 系列
- **计算机视觉**: ViT、DETR
- **多模态**: CLIP、GPT-4V

## 相关概念
- [[Self-Attention]] — Transformer 的核心机制
- [[Multi-head Attention]] — 多头注意力
- [[Positional Encoding]] — 位置编码
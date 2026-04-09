---
title: "Transformer"
type: concept
tags: ["Transformer", "Self-Attention", "Neural Network", "Deep Learning"]
date: 2026-04-09
---

## Definition
Transformer 是一种基于自注意力机制（Self-Attention）的神经网络架构，由 Vaswani 等人在 2017 年论文《Attention Is All You Need》中提出。它完全摒弃了传统的循环神经网络结构，采用注意力机制并行处理序列数据。

## Core Components
- **多头注意力机制（Multi-Head Attention）**：并行计算多个注意力头，捕获不同层面的依赖关系
- **前馈神经网络（Feed-Forward Network）**：每个位置独立进行非线性变换
- **位置编码（Positional Encoding）**：注入序列位置信息
- **层归一化（Layer Normalization）**：稳定训练过程
- **残差连接（Residual Connection）**：缓解梯度消失问题

## Key Innovations
- 完全并行化处理，显著提升训练效率
- 长距离依赖建模能力强
- 可扩展性强，支持大规模预训练

## Applications
- **NLP**：BERT、GPT 系列、T5
- **Computer Vision**：ViT、DETR、Stable Diffusion
- **Multimodal**：CLIP、GPT-4V、Gemini
- **Speech**：Whisper、Wav2Vec

## Related Sources
- [[transformer-intro]] — Transformer 介绍
- [[transformer-intro-v2]] — Transformer 详解

## Related Entities
- [[Vaswani]] — 论文作者
- [[BERT]] — 基于 Transformer 的模型
- [[GPT]] — 基于 Transformer 的模型

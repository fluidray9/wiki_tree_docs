---
title: "Kubernetes (K8s)"
type: source
tags: []
date: 2026-04-09
source_file: raw/kubernetes.md
---

## Summary
Kubernetes (K8s) is an open-source system for managing containerized applications across multiple hosts, providing mechanisms for deployment, maintenance, and scaling. It was built on over a decade and a half of experience at Google running production workloads at scale using an internal system called Borg, combined with community best practices. Kubernetes is hosted by the Cloud Native Computing Foundation (CNCF) and is the foundational platform for cloud-native microservices architectures.

## Key Claims
- **Container orchestration**: Kubernetes manages containerized applications across multiple hosts, handling deployment, maintenance, and scaling automatically
- **Borg heritage**: Built from Google's internal Borg system, proven at massive scale in production for 15+ years
- **CNCF-hosted**: Operated under the Cloud Native Computing Foundation governance, along with hundreds of other cloud-native projects
- **Multi-environment development**: Can be built from source using either a Go development environment or a Docker environment via `make` and `make quick-release` respectively
- **Library disclaimer**: The `k8s.io/kubernetes` module is not supported for use as a library in external applications; a separate list of published staging components is available
- **Governance**: Governed by a Steering Committee that oversees the project's principles, values, and processes
- **Community transparency**: Roadmap and feature tracking are publicly available via the Kubernetes Enhancements repository

## Key Quotes
> "Kubernetes builds upon a decade and a half of experience at Google running production workloads at scale using a system called Borg, combined with best-of-breed ideas and practices from the community." — Kubernetes README
> "Kubernetes, also known as K8s, is an open source system for managing containerized applications across multiple hosts. It provides basic mechanisms for the deployment, maintenance, and scaling of applications." — Kubernetes README

## Connections
- [[CNCF]] — The Cloud Native Computing Foundation that hosts and governs the Kubernetes project; Kubernetes is the founding project of CNCF
- [[Linux]] — Kubernetes runs on Linux and relies on Linux kernel features (cgroups, namespaces) for container isolation; often deployed on Linux servers in production
- [[Docker]] — Container runtime that Kubernetes orchestrates; Docker containers are the primary workload type managed by Kubernetes; Docker is required for building Kubernetes from source (`make quick-release`)
- [[Go]] — The language in which Kubernetes is written; a working Go environment is one of two ways to build Kubernetes from source
- [[DevContainers]] — Dev Containers and cloud development environments can host Kubernetes-based development workflows
- [[Claude Code]] — Claude Code can be used to develop, configure, and maintain Kubernetes-based applications and infrastructure-as-code
- [[MicroservicesArchitecture]] — Kubernetes is the canonical platform for deploying and orchestrating microservices-based applications at scale

## Contradictions
- No direct contradictions with existing sources. Kubernetes complements [[Linux]] (runtime platform), [[Docker]] (container runtime), and [[Visual-Studio-Code]]/[[Claude-Code]] (development tools) as part of a complete cloud-native stack.

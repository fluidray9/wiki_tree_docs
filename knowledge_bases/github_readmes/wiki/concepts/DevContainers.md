---
title: "Dev Containers"
type: concept
tags: []
date: 2026-04-09
---

## Summary
Dev Containers enable reproducible, containerized development environments directly within an IDE or editor. VS Code supports Dev Containers (via the Dev Containers extension) and GitHub Codespaces, allowing developers to spin up a fully configured environment from a Dockerfile in the repository with a single action.

## Key Characteristics
- **Container-based**: Development runs inside a Docker container with consistent tooling
- **Reproducible**: Every developer (or Codespace) gets the same environment defined by configuration files
- **IDE integration**: VS Code opens the container as the working directory, providing full editing, debugging, and terminal support
- **Codespaces option**: Cloud-hosted development environments via GitHub Codespaces, requiring only a browser or VS Code desktop client
- **Resource requirements**: Full build of VS Code from source in a container requires at least 4 CPU cores and 6 GB RAM (8 GB recommended)

## Connections
- [[Visual Studio Code]] — the host IDE with native Dev Containers and Codespaces support
- [[Claude Code]] — can operate within a Dev Container environment to provide agentic coding assistance alongside VS Code

## Connections (additional)
- [[Visual Studio Code]] — the host IDE with native Dev Containers and Codespaces support
- [[Claude Code]] — can operate within a Dev Container environment to provide agentic coding assistance alongside VS Code
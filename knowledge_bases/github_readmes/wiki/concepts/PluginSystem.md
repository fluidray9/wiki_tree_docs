---
title: "Plugin System"
type: concept
tags: []
date: 2026-04-09
---

## Summary
A plugin system allows an application to be extended with custom commands, agents, and integrations without modifying its core codebase. Claude Code implements this pattern to let developers add domain-specific workflows and tooling.

## Key Characteristics
- **Custom commands**: Developer-defined slash commands that invoke specific behaviors
- **Custom agents**: Specialized AI agents tailored to particular tasks or domains
- **Isolation**: Plugins extend functionality without coupling to core logic
- **Repository-based distribution**: Plugins are distributed via the Claude Code plugins directory

## Connections
- [[Claude Code]] — the host application that supports plugins
- [[AgenticCodingTool]] — plugin systems enhance the autonomy and scope of agentic tools

## Connections (additional)
- [[Claude Code]] — the host application that supports plugins
- [[AgenticCodingTool]] — plugin systems enhance the autonomy and scope of agentic tools
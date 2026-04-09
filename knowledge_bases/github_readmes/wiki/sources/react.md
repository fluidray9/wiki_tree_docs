---
title: "React"
type: source
tags: []
date: 2026-04-09
source_file: raw/react.md
---

## Summary
React is a JavaScript library for building user interfaces, developed and maintained by [[Meta]] (Facebook). It emphasizes a declarative, component-based programming model that makes interactive UIs predictable and easy to reason about. React is designed for gradual adoption — developers can use as little or as much of it as needed — and follows a "Learn Once, Write Anywhere" philosophy, extending from the web (with [[Node]] server-side rendering) to mobile (via [[React-Native]]).

## Key Claims
- **Declarative**: React lets developers design simple views for each application state and efficiently updates only the right components when data changes, making code more predictable and easier to debug
- **Component-Based**: Encapsulated components manage their own state and compose into complex UIs, with all logic written in JavaScript (not templates)
- **Learn Once, Write Anywhere**: No assumptions about the rest of the technology stack; can render on the server via Node and power mobile apps with React Native
- **Gradual Adoption**: Designed for incremental adoption — developers can introduce React to existing projects without rewriting code
- **MIT Licensed**: React is open-source under the MIT license
- **JSX Optional but Recommended**: JSX syntax looks like HTML and makes code more readable, though it is not required to use React
- **Community and Contribution**: Development happens in the open on GitHub; contributions are welcome with a Code of Conduct and "good first issue" labels
- **Security Reporting**: Security vulnerabilities must be reported privately via email, not as public GitHub issues

## Key Quotes
> "React makes it painless to create interactive UIs. Design simple views for each state in your application, and React will efficiently update and render just the right components when your data changes." — React README
> "We don't make assumptions about the rest of your technology stack, so you can develop new features in React without rewriting existing code." — React README
> "You'll notice that we used an HTML-like syntax; we call it JSX. JSX is not required to use React, but it makes code more readable, and writing it feels like writing HTML." — React README

## Connections
- [[Meta]] — the company (Facebook) that develops and maintains React; has adopted a Code of Conduct for contributors
- [[React-Native]] — React's approach to mobile development: "Learn Once, Write Anywhere" extends to powering native mobile apps
- [[Node]] — React can render on the server using Node, enabling server-side rendering (SSR) and full-stack architectures
- [[Next-js]] — Next.js is a React framework that builds on React's component model, adding SSR, routing, and full-stack capabilities; React is a dependency of Next.js
- [[Visual-Studio-Code]] — VS Code is a commonly-used cross-platform editor/IDE for writing React applications, with React extensions providing IntelliSense and debugging support
- [[Claude-Code]] — React and its framework ecosystem (Next.js, etc.) are a natural target for Claude Code's agentic coding assistance; building React UIs involves creating components, managing state, and wiring JSX — all areas where AI coding tools can accelerate development
- [[JavaScript-Ecosystem]] — React is a foundational library in the modern JavaScript ecosystem, alongside frameworks like Vue, Angular, and Svelte

## Contradictions
- No direct contradictions with existing sources. React and [[Next-js]] have a parent-framework relationship (Next.js extends React). React and [[Visual-Studio-Code]] are complementary (library vs. editor). [[Claude-Code]] and React are also complementary (agentic coding tool vs. target library/framework).
# Overview

Knowledge base: github_readmes

## At a Glance
This knowledge base catalogs GitHub README documents for notable open-source developer tools and platforms, plus meta-documentation for the wiki-tree-docs project itself.

## Topics Covered

### Wiki & Developer Workflow
- **Wiki Tree Docs** — A multi-knowledge-base skill for AI coding agents. Each knowledge base has its own raw/, wiki/, and tree/ workspace. The system provides slash commands (init, list, use, delete, ingest, query, lint, graph), a set of Python tools scripts, and supports any Anthropic API-compatible provider. Key concepts include the wiki index (structured cross-referenced pages), the tree index (hierarchical JSON with section-level granularity), and a meta.json at the repo root for alias mapping and default knowledge base. Designed for LLM-centric documentation workflows — open the repo in Claude Code and no API key or scripts are needed.

### Operating Systems & Low-Level Development
- **Linux Kernel** — The open-source core of the Linux operating system, maintained by Linus Torvalds and a global contributor community. Development follows a mailing-list-based patch submission workflow (lore.kernel.org) entirely different from GitHub pull-request models. Key processes include the Developer Certificate of Origin (DCO) requiring Signed-off-by on every commit, strict kernel coding style documentation, and an explicit AI Coding Assistant mandate requiring LLMs to read Documentation/process/coding-assistants.rst before contributing. Security follows an embargoed disclosure process for hardware vulnerabilities. Hardware support spans servers, embedded devices, and Android (where Linux powers the OS).

### Developer Tools
- **Claude Code** — An agentic coding tool by [[Anthropic]] that operates in the terminal, understands your codebase, and accelerates development through natural language commands. Key capabilities include executing routine tasks, explaining complex code, and managing git workflows. Supports MacOS/Linux (curl script, Homebrew) and Windows (PowerShell, WinGet). Has a plugin system for extensibility. npm installation is deprecated. Data collection covers usage events and bug reports, but explicitly excludes use for model training.
- **Visual Studio Code** — A cross-platform code editor by [[Microsoft]] built on the open-source "Code - OSS" repository. Combines a lightweight code editor with edit-build-debug cycle support, comprehensive language services, a rich extensibility model, and Dev Containers/GitHub Codespaces integration. Updated monthly; roadmap and iteration plans are published publicly on GitHub. MIT licensed for OSS components.
- **Next.js** — A React meta-framework by [[Vercel]] for building full-stack web applications, extending the latest React features with powerful Rust-based JavaScript tooling (Turbopack) for fast builds. Used by large companies worldwide. Community is active on GitHub Discussions and Discord; contributions are welcomed via "good first issues."
- **React** — A JavaScript library by [[Meta]] (formerly Facebook) for building user interfaces with a declarative, component-based model. Core principles include Declarative UI (describe what the UI should look like per state), Component-Based Architecture (self-contained, reusable components), and "Learn Once, Write Anywhere" (from web server rendering via [[Node]] to mobile via [[React-Native]]). JSX syntax is recommended but optional. MIT licensed; contributions and security reporting are handled through GitHub and private email channels respectively.

## Key Themes
- Shift toward agentic AI tools that autonomously execute tasks rather than just providing suggestions
- Cross-platform support as a standard expectation for developer tooling
- Community-driven development via Discord and GitHub issue tracking
- Explicit data privacy commitments (no training on user feedback) as a differentiator
- IDE extensibility as a core platform strategy — both VS Code (extension API) and Claude Code (plugin system) enable community contributions
- Dev Containers and cloud development environments (Codespaces) as the next evolution in reproducible, team-consistent development setups
- Open-source core (Code - OSS) paired with proprietary add-ons as a sustainable open-core business model for developer tooling
- Rust-based JavaScript tooling (Turbopack) as the emerging performance standard for build pipelines in the React ecosystem
- Full-stack web frameworks collapsing the traditional frontend/backend boundary into unified, opinionated project structures
- Declarative, component-based UI architecture as the dominant paradigm for modern front-end development, replacing imperative DOM manipulation
- "Learn Once, Write Anywhere" platforms (React → React Native) as a strategy to maximize code sharing across web and mobile without rewriting logic
- The Linux kernel as the canonical example of a mature, large-scale open-source project with a patch-based, mailing-list workflow fundamentally different from GitHub-centric contribution models
- Explicit AI/LLM compliance requirements (DCO, coding-assistants documentation) emerging as a new dimension of open-source contribution governance, as demonstrated by the Linux kernel's AI Coding Assistant section

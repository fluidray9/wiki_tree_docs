---
title: "JSX"
type: concept
tags: []
date: 2026-04-09
---

## Summary
JSX (JavaScript XML) is a syntax extension for JavaScript that allows developers to write HTML-like markup directly inside JavaScript code. It is used by React to describe what the UI should look like. JSX is not required to use React — React can work with plain JavaScript `createElement` calls — but JSX makes component code more readable and is the conventional way to write React applications.

## Key Characteristics
- Looks like HTML but is JavaScript: allows HTML-like tags, attributes, and children inside JavaScript expressions
- Expressions can be embedded using curly braces `{}`: e.g., `<div>Hello {name}</div>`
- JSX is transpiled by tools like Babel into `React.createElement()` calls
- Makes component logic (JavaScript) and UI structure (markup) co-located, improving readability and maintainability
- React's documentation recommends JSX as the preferred way to describe UI, even though it is technically optional

## Connections
- [[React]] — JSX was popularized by React and is the standard syntax for writing React components
- [[JavaScript-Ecosystem]] — JSX is part of the broader JavaScript tooling ecosystem, requiring a transpiler (Babel, TypeScript, SWC) in most build pipelines

## Connections (additional)
- [[React]] — JSX was popularized by React and is the standard syntax for writing React components
- [[JavaScript-Ecosystem]] — JSX is part of the broader JavaScript tooling ecosystem, requiring a transpiler (Babel, TypeScript, SWC) in most build pipelines
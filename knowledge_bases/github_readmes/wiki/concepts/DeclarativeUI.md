---
title: "Declarative UI"
type: concept
tags: []
date: 2026-04-09
---

## Summary
Declarative UI is a programming paradigm in which developers describe *what* the UI should look like for a given state, rather than imperatively specifying the step-by-step instructions to manipulate the DOM. React popularized this approach in the JavaScript ecosystem: developers declare the desired view for each application state, and React efficiently updates the actual DOM to match. This makes code more predictable, easier to reason about, and easier to debug compared to imperative UI manipulation.

## Key Characteristics
- **State-driven**: The UI is a function of state — when state changes, the UI re-renders to reflect the new state
- **Predictability**: Because the UI is a deterministic output of the state, it is easier to reason about than imperative DOM manipulation
- **Efficiency**: Declarative frameworks like React use virtual DOM diffing to minimize actual DOM mutations, improving performance
- **Contrast with imperative UI**: Imperative code explicitly calls DOM APIs (e.g., `element.appendChild()`, `node.removeChild()`), which becomes hard to maintain at scale

## Connections
- [[React]] — React is the canonical declarative UI library in the JavaScript ecosystem, championing this paradigm
- [[Component-Based-Architecture]] — Declarative UI is enabled by React's component model: each component declares its view based on its props and state
- [[React-Native]] — The declarative paradigm extends to mobile via React Native

## Connections (additional)
- [[React]] — React is the canonical declarative UI library in the JavaScript ecosystem, championing this paradigm
- [[Component-Based-Architecture]] — Declarative UI is enabled by React's component model: each component declares its view based on its props and state
- [[React-Native]] — The declarative paradigm extends to mobile via React Native
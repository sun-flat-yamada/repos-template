---
title: 'Language Coding Rules: JavaScript'
description: Language-specific style guidelines, static analysis requirements, and
  best practices for JavaScript.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- language-rules
- javascript
alwaysApply: false
globs:
- '**/*.js'
- '**/*.jsx'
- '**/*.mjs'
- '**/*.cjs'
- '**/package.json'
---
# Language Coding Rules: JavaScript (`coding-rules-javascript`)

## 1. Modern Syntax & Standards
- Target ECMAScript 2024+ with pure ESM (`import` / `export`). Prohibit legacy CommonJS (`require`).
- Use `const` by default; use `let` only when reassignment is strictly required. Prohibit `var`.
- Use optional chaining (`obj?.prop`) and nullish coalescing (`a ?? b`) instead of loose boolean short-circuiting.

## 2. Defensive Practices
- Validate all arguments at function boundaries when building public or cross-module interfaces.
- Avoid prototype pollution: use `Object.create(null)` or `Map` for arbitrary key-value mappings.
- Provide comprehensive JSDoc comments (`@param {string} name`, `@returns {Promise<boolean>}`).

## 3. Tooling & Enforcement
- Enforce clean style and zero unused variables using ESLint or Biome.
- Test suites: execute using native Node.js runner (`node --test`) or Vitest.

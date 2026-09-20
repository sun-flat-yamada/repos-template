---
title: 'Language Coding Rules: TypeScript'
description: Language-specific style guidelines, static analysis requirements, and
  best practices for TypeScript.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- language-rules
- typescript
alwaysApply: false
globs:
- '**/*.ts'
- '**/*.tsx'
- '**/tsconfig*.json'
- '**/package.json'
---
# Language Coding Rules: TypeScript (`coding-rules-typescript`)

## 1. Type Strictness & Safety
- **Strict Mode**: Maintain `"strict": true` in `tsconfig.json`.
- **Ban `any`**: The `any` type is prohibited. Use `unknown` with runtime parsing (Zod, ArkType) for untrusted data.
- **Type Guards**: Use custom type guard functions (`is Foo`) or discriminated unions to narrow types.
- **Immutable Types**: Prefer `readonly` arrays (`readonly string[]` or `ReadonlyArray<T>`) and `as const` assertions for literal values.

## 2. Functions & Architecture
- Prefer explicit function return types on exported APIs to prevent inadvertent type regressions.
- Use async/await over raw `.then()` / `.catch()` promise chaining.
- Structure projects using pure ESM (`"type": "module"` in `package.json`).

## 3. Tooling & Enforcement
- Run `eslint` (or Biome) and `tsc --noEmit` in CI.
- Format code automatically using Prettier or Biome.

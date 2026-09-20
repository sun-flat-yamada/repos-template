---
title: 'Code Review Profile: TypeScript'
description: Auditing standards, idiomatic patterns, memory safety, and common anti-patterns
  for TypeScript codebases.
category: agent-profile
type: review-profile
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- agent
- profile
- code-review
- typescript
alwaysApply: false
globs:
- '**/*.ts'
- '**/*.tsx'
- '**/tsconfig*.json'
- '**/package.json'
---
# Code Review Profile: TypeScript (`code-review-profile-typescript`)

Focus on high-impact defects and runtime safety. Disregard formatting (entrusted to Biome/Prettier).

---

## 🔍 High-Signal Review Checklist

### 1. Runtime Type Integrity
- [ ] **[P0-BLOCKER] Fake Type Assertion (`as T`)**: Does the code use `as T` on external inputs (HTTP responses, database records, file reads) without runtime schema parsing?
- [ ] **[P1-DEFECT] Leaked `any`**: Does any function return or accept `any`? Does third-party library interop introduce unconstrained `any` into internal domain logic?
- [ ] **[P1-DEFECT] Non-Exhaustive Union Matching**: In switch/if ladders handling discriminated unions, is there an `assertNever` default branch ensuring compiler errors when new variants are added?

### 2. Asynchronous Reliability
- [ ] **[P0-BLOCKER] Floating Promise**: Is any function returning a `Promise` invoked without `await` or `void ... .catch()`?
- [ ] **[P1-DEFECT] Async Callback in `forEach`**: Is an async callback passed to `arr.forEach(...)`? (It does NOT await promises sequentially; use `for...of` or `Promise.all`).

### 3. Edge Cases & Optional Access
- [ ] **[P1-DEFECT] Unchecked Index Access**: Does array indexing (`arr[0]`) assume existence without nullish check or length verification?
- [ ] **[P2-MAINTENANCE] Loose Equality**: Flag any `==` or `!=`; enforce strict `===` and `!==`.

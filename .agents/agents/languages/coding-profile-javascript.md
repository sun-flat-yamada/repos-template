---
title: 'Coding Profile: JavaScript'
description: Production implementation standards, architectural idioms, dependency
  hygiene, and testing guidelines for JavaScript.
category: agent-profile
type: coding-profile
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- agent
- profile
- coding
- javascript
alwaysApply: false
globs:
- '**/*.js'
- '**/*.jsx'
- '**/*.mjs'
- '**/*.cjs'
- '**/package.json'
---
# Coding Profile: JavaScript (`coding-profile-javascript`)

## Target Standards
- **Standard Version**: ECMAScript 2024+ (Node 20+)
- **Primary Toolchain**: Node.js Test Runner / Vitest, Biome / ESLint

---

## 🎯 Critical Engineering Safeguards (High-Impact Idioms)

### 1. Prototype Pollution Defense
- **Rule**: Never merge or assign untrusted JSON keys onto plain JavaScript objects without sanitizing `__proto__`, `constructor`, and `prototype`.
- **Anti-Pattern (Security Vulnerability)**:
  ```javascript
  // BAD: Malicious payload {"__proto__": {"isAdmin": true}} pollutes all objects!
  function deepMerge(target, source) {
      for (const key in source) {
          target[key] = source[key];
      }
  }
  ```
- **Resilient Idiom**:
  ```javascript
  // GOOD: Create objects without prototype or sanitize forbidden keys
  const safeMap = Object.create(null);
  // Or check against prototype keys:
  if (key === "__proto__" || key === "constructor" || key === "prototype") {
      continue;
  }
  ```

### 2. Regular Expression Denial of Service (ReDoS) Defense
- **Rule**: Avoid nested quantifiers in regular expressions (e.g. `(a+)+`, `([a-zA-Z]+)*`). They exhibit exponential backtracking on untrusted user inputs.
- **Idiom**: Use linear-time parsers or validate regex execution limits.

### 3. Strict Equality & Coercion Defense
- **Rule**: Always use `===` and `!==`. Prohibit loose equality `==` which triggers surprising type coercion (e.g. `"" == 0` is true).

### 4. Banned Antipatterns
- Modifying built-in prototypes (`Array.prototype.customMethod = ...`).
- Using `var`. Use `const` by default, `let` only when reassigning.

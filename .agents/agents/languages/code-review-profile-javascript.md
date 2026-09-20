---
title: 'Code Review Profile: JavaScript'
description: Auditing standards, idiomatic patterns, memory safety, and common anti-patterns
  for JavaScript codebases.
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
- javascript
alwaysApply: false
globs:
- '**/*.js'
- '**/*.jsx'
- '**/*.mjs'
- '**/*.cjs'
- '**/package.json'
---
# Code Review Profile: JavaScript (`code-review-profile-javascript`)

Focus on prototype pollution, ReDoS vulnerabilities, and async promise discipline.

---

## 🔍 High-Signal Review Checklist

### 1. Security & Prototype Safety
- [ ] **[P0-BLOCKER] Prototype Pollution**: Does recursive object copying or deep merging handle `__proto__`, `prototype`, or `constructor` without filtering?
- [ ] **[P0-BLOCKER] ReDoS Hazard**: Does any regular expression match untrusted user input using nested quantifiers (`(a+)+`)?
- [ ] **[P0-BLOCKER] Dynamic Code Execution**: Does code call `eval()`, `new Function()`, or `setTimeout(string)`?

### 2. Async Hygiene & Errors
- [ ] **[P1-DEFECT] Floating Promise**: Are promises left unawaited and unhandled, risking `UnhandledPromiseRejection`?
- [ ] **[P1-DEFECT] Loose Equality (`==`)**: Are loose equality checks used? (Must be `===` or `Object.is()`).

### 3. Module & Scope Hygiene
- [ ] **[P1-DEFECT] CommonJS Leaked in ESM**: Are `require()` or `module.exports` used in pure ESM projects?
- [ ] **[P2-MAINTENANCE] Global Prototype Mutation**: Does any code extend or mutate built-in JavaScript prototypes?

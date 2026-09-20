---
title: 'Code Review Profile: C'
description: Auditing standards, idiomatic patterns, memory safety, and common anti-patterns
  for C codebases.
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
- c
alwaysApply: false
globs:
- '**/*.c'
- '**/*.h'
- '**/Makefile'
- '**/CMakeLists.txt'
---
# Code Review Profile: C (`code-review-profile-c`)

Focus on memory safety vulnerabilities, undefined behavior, and buffer management.

---

## 🔍 High-Signal Review Checklist

### 1. Memory Safety & Leaks
- [ ] **[P0-BLOCKER] Direct `realloc` Assignment**: Is `ptr = realloc(ptr, ...)` used directly without a temporary pointer check?
- [ ] **[P0-BLOCKER] Use-After-Free / Double-Free**: Is memory freed multiple times, or accessed after `free()`? Are freed pointers assigned to `NULL`?
- [ ] **[P0-BLOCKER] Missing `malloc` NULL Check**: Is the return value of `malloc`/`calloc` dereferenced without a `NULL` verification?

### 2. Buffer Overflows & String Handling
- [ ] **[P0-BLOCKER] Banned Function Call**: Does code invoke `gets`, `strcpy`, `strcat`, or `sprintf`?
- [ ] **[P1-DEFECT] Missing Null Termination**: When manipulating byte arrays or buffers, is the null terminator `\0` explicitly guaranteed at the final index?
- [ ] **[P1-DEFECT] Snprintf Return Value Misuse**: Is `snprintf` return value used as a buffer offset without checking `(size_t)n < sizeof(buf)`?

### 3. Concurrency & Signals
- [ ] **[P0-BLOCKER] Unsafe Signal Handler**: Are `printf`, `malloc`, or mutex calls made within a POSIX signal handler? (Must only invoke async-signal-safe functions).

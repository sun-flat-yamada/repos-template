---
title: 'Code Review Profile: Go'
description: Auditing standards, idiomatic patterns, memory safety, and common anti-patterns
  for Go codebases.
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
- go
alwaysApply: false
globs:
- '**/*.go'
- '**/go.mod'
- '**/go.sum'
---
# Code Review Profile: Go (`code-review-profile-go`)

Focus on goroutine leaks, synchronization bugs, and error handling correctness.

---

## 🔍 High-Signal Review Checklist

### 1. Concurrency & Goroutines
- [ ] **[P0-BLOCKER] Goroutine Leak**: Does any spawned goroutine write to an unbuffered channel without selecting on `ctx.Done()`?
- [ ] **[P0-BLOCKER] Defer in Loop**: Is `defer mu.Unlock()` or `defer file.Close()` called inside a loop iteration? (Causes severe lock contention or file descriptor exhaustion).
- [ ] **[P0-BLOCKER] Data Race**: Does code read/write shared variables across goroutines without atomics or mutex? (Must pass `go test -race`).

### 2. Resource Management
- [ ] **[P0-BLOCKER] Unclosed Response Body**: Is `resp.Body.Close()` missing after `http.Get` / `client.Do`?
- [ ] **[P1-DEFECT] Context Omission**: Do database, network, or external client operations omit `context.Context`?

### 3. Error Handling
- [ ] **[P1-DEFECT] Fragile Error Comparison**: Is `err == ErrX` used instead of `errors.Is(err, ErrX)`?
- [ ] **[P1-DEFECT] Blind Error Ignore**: Is any error ignored using `_ = fn()` without an explicit comment explaining why failure is impossible or harmless?

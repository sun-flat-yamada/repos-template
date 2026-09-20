---
title: 'Code Review Profile: Rust'
description: Auditing standards, idiomatic patterns, memory safety, and common anti-patterns
  for Rust codebases.
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
- rust
alwaysApply: false
globs:
- '**/*.rs'
- '**/Cargo.toml'
- '**/Cargo.lock'
---
# Code Review Profile: Rust (`code-review-profile-rust`)

Focus on safety invariants, concurrency deadlocks, and cancellation hazards. Disregard formatting (entrusted to `cargo fmt`).

---

## 🔍 High-Signal Review Checklist

### 1. Concurrency & Deadlocks
- [ ] **[P0-BLOCKER] Sync Mutex Across Await**: Is `std::sync::MutexGuard` held across an `.await` call? (Must be replaced with `tokio::sync::Mutex` or scoped release).
- [ ] **[P0-BLOCKER] Select Cancellation Hazard**: Does any `tokio::select!` branch operate on an operation that is NOT cancellation-safe (e.g. stateful partial reads)?
- [ ] **[P1-DEFECT] Blocking Code in Async Runtime**: Is heavy CPU work or blocking file I/O executed on the async worker pool without `tokio::task::spawn_blocking`?

### 2. Panic & Error Propagation
- [ ] **[P0-BLOCKER] Unchecked Panic in Production**: Does any non-test code call `.unwrap()`, `.expect()`, `unreachable!()`, or index an array without boundary bounds?
- [ ] **[P1-DEFECT] Error Swallowing**: Are `Result` or `Option` values discarded using `let _ = ...` without logging or rationale?

### 3. Memory & Unsafe
- [ ] **[P0-BLOCKER] Unverified Unsafe**: Does any `unsafe` block omit a detailed `// SAFETY:` rationale explaining why invariants cannot be violated?
- [ ] **[P2-MAINTENANCE] Excessive Allocation**: Are `.clone()` or `.to_string()` called repeatedly in tight loops where borrowing (`&str`, `&[T]`) suffices?

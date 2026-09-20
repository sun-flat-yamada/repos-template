---
title: 'Language Coding Rules: Rust'
description: Language-specific style guidelines, static analysis requirements, and
  best practices for Rust.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- language-rules
- rust
alwaysApply: false
globs:
- '**/*.rs'
- '**/Cargo.toml'
- '**/Cargo.lock'
---
# Language Coding Rules: Rust (`coding-rules-rust`)

## 1. Safety, Ownership & Borrowing
- **Zero Panics in Production**: Avoid `.unwrap()` and `.expect()` in non-test code. Propagate errors via `Result<T, E>` and `?`.
- **Minimal `unsafe`**: Any `unsafe` block must be strictly scoped and documented with a mandatory `// SAFETY:` rationale explaining invariants.
- **Idiomatic Lifetimes & Ownership**: Prefer borrowing over ownership transfer when values are only read. Avoid unnecessary allocations (`to_string()`, `clone()`).

## 2. Types & Idioms
- Represent invalid states as unrepresentable types using Rust enums.
- Use the Newtype pattern (`struct UserId(u64);`) to enforce domain type safety.
- Implement standard traits: `Debug`, `Clone`, `Default`, `PartialEq`, `Display`.

## 3. Tooling & Enforcement
- Run `cargo clippy --all-targets --all-features -- -D warnings` in CI.
- Check formatting with `cargo fmt --check`.
- Execute tests with `cargo test --all-targets`.

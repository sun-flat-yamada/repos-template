---
title: 'Coding Profile: Rust'
description: Production implementation standards, architectural idioms, dependency
  hygiene, and testing guidelines for Rust.
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
- rust
alwaysApply: false
globs:
- '**/*.rs'
- '**/Cargo.toml'
- '**/Cargo.lock'
---
# Coding Profile: Rust (`coding-profile-rust`)

## Target Standards
- **Standard Version**: Rust 2021 Edition / Rust 1.80+
- **Primary Toolchain**: `cargo clippy -- -D warnings`, `cargo test`, `cargo fmt`

---

## 🎯 Critical Engineering Safeguards (High-Impact Idioms)

### 1. Cancellation Safety in Async (`tokio::select!`)
- **Rule**: Branches inside `tokio::select!` must be cancellation-safe. If a future is cancelled mid-execution, state must not become corrupted.
- **Anti-Pattern (Cancellation Hazard)**:
  ```rust
  // BAD: If cancelled after read_exact finishes but before write_all completes, data is lost
  tokio::select! {
      res = socket.read_exact(&mut buf) => { ... }
      _ = timeout => { ... }
  }
  ```
- **Resilient Idiom**:
  Use framed streams or dedicated actors where incomplete reads do not corrupt the message stream.

### 2. Lock Hygiene & Async Deadlock Defense
- **Rule**: NEVER hold a standard synchronous lock (`std::sync::MutexGuard`) across an `.await` point. Use `tokio::sync::Mutex` or restructure code to release the lock before awaiting.
- **Anti-Pattern (Async Deadlock)**:
  ```rust
  // BAD: Holds std::sync mutex across await; causes thread-pool starvation / deadlocks
  let mut guard = std_mutex.lock().unwrap();
  guard.data = fetch_remote().await?; 
  ```
- **Resilient Idiom**:
  ```rust
  // GOOD: Keep lock scope minimal and non-async
  let data = fetch_remote().await?;
  {
      let mut guard = std_mutex.lock().unwrap();
      guard.data = data;
  }
  ```

### 3. Error Handling without Panics
- **Rule**: Zero `.unwrap()` or `.expect()` in library, production, or network-handling code. Always propagate errors using `Result<T, E>` and `?`.
- **Idiom**: Use `thiserror` for domain/library error enums and `anyhow` for CLI/applications.

### 4. Banned Antipatterns
- Unjustified `.clone()` to bypass borrow checker without architectural necessity.
- Undocumented `unsafe` blocks. Every `unsafe` block must have a `// SAFETY:` invariant comment.

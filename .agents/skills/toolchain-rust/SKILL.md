---
name: "toolchain-rust"
description: "Executes Cargo toolchains for Rust including cargo check, cargo test, cargo clippy, and cargo fmt formatting."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.rs"
  - "**/Cargo.toml"
  - "**/Cargo.lock"
tags:
  - "skill"
  - "toolchain"
  - "rust"
  - "build"
  - "test"
---
# Skill: Rust Toolchain (`toolchain-rust`)

## Instructions
1. **Compilation Check**:
   ```bash
   cargo check --all-targets --all-features
   ```
2. **Linting & Formatting**:
   ```bash
   cargo fmt --check
   cargo clippy --all-targets --all-features -- -D warnings
   ```
3. **Automated Testing**:
   ```bash
   cargo test --all-targets --all-features
   ```

## Best Practices
- Treat all Clippy warnings as fatal errors (`-D warnings`).
- Verify zero panicking `.unwrap()` calls exist outside unit tests.

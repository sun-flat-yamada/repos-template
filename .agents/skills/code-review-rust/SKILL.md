---
name: "code-review-rust"
description: "Audits RUST source code diffs against language-specific idioms, memory safety, static analysis, and code-review-profile-rust.md."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.rs"
  - "**/Cargo.toml"
  - "**/Cargo.lock"
tags:
  - "skill"
  - "code-review"
  - "rust"
  - "quality-gate"
---
# Skill: High-Signal Code Review for RUST (`code-review-rust`)

## Instructions
1. **Profile Inspection**:
   - Evaluate all modified `RUST` files against the high-impact checklist in `.agents/agents/languages/code-review-profile-rust.md` and coding rules in `.agents/rules/languages/coding-rules-rust.md`.
2. **Execute Static Analysis & Toolchain Verification**:
   - Run: `cargo clippy -- -D warnings and cargo test` using `toolchain-rust`.
   - Confirm zero unhandled warnings or fatal analyzer errors.
3. **Classify by Severity**:
   - Flag issues using `[P0-BLOCKER]`, `[P1-DEFECT]`, or `[P2-MAINTENANCE]`.
   - Provide concrete before/after code snippets for every P0 and P1 finding.
4. **Issue Final Rubric Verdict**:
   - Aggregate evaluation into `code-review-gatekeeper` format.

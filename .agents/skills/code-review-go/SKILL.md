---
name: "code-review-go"
description: "Audits GO source code diffs against language-specific idioms, memory safety, static analysis, and code-review-profile-go.md."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.go"
  - "**/go.mod"
  - "**/go.sum"
tags:
  - "skill"
  - "code-review"
  - "go"
  - "quality-gate"
---
# Skill: High-Signal Code Review for GO (`code-review-go`)

## Instructions
1. **Profile Inspection**:
   - Evaluate all modified `GO` files against the high-impact checklist in `.agents/agents/languages/code-review-profile-go.md` and coding rules in `.agents/rules/languages/coding-rules-go.md`.
2. **Execute Static Analysis & Toolchain Verification**:
   - Run: `golangci-lint run and go test -race ./...` using `toolchain-go`.
   - Confirm zero unhandled warnings or fatal analyzer errors.
3. **Classify by Severity**:
   - Flag issues using `[P0-BLOCKER]`, `[P1-DEFECT]`, or `[P2-MAINTENANCE]`.
   - Provide concrete before/after code snippets for every P0 and P1 finding.
4. **Issue Final Rubric Verdict**:
   - Aggregate evaluation into `code-review-gatekeeper` format.

---
name: "code-review-javascript"
description: "Audits JAVASCRIPT source code diffs against language-specific idioms, memory safety, static analysis, and code-review-profile-javascript.md."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.mjs"
  - "**/*.cjs"
  - "**/package.json"
tags:
  - "skill"
  - "code-review"
  - "javascript"
  - "quality-gate"
---
# Skill: High-Signal Code Review for JAVASCRIPT (`code-review-javascript`)

## Instructions
1. **Profile Inspection**:
   - Evaluate all modified `JAVASCRIPT` files against the high-impact checklist in `.agents/agents/languages/code-review-profile-javascript.md` and coding rules in `.agents/rules/languages/coding-rules-javascript.md`.
2. **Execute Static Analysis & Toolchain Verification**:
   - Run: `eslint/biome check and node --test` using `toolchain-javascript`.
   - Confirm zero unhandled warnings or fatal analyzer errors.
3. **Classify by Severity**:
   - Flag issues using `[P0-BLOCKER]`, `[P1-DEFECT]`, or `[P2-MAINTENANCE]`.
   - Provide concrete before/after code snippets for every P0 and P1 finding.
4. **Issue Final Rubric Verdict**:
   - Aggregate evaluation into `code-review-gatekeeper` format.

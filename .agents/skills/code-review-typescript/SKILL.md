---
name: "code-review-typescript"
description: "Audits TYPESCRIPT source code diffs against language-specific idioms, memory safety, static analysis, and code-review-profile-typescript.md."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/tsconfig*.json"
  - "**/package.json"
tags:
  - "skill"
  - "code-review"
  - "typescript"
  - "quality-gate"
---
# Skill: High-Signal Code Review for TYPESCRIPT (`code-review-typescript`)

## Instructions
1. **Profile Inspection**:
   - Evaluate all modified `TYPESCRIPT` files against the high-impact checklist in `.agents/agents/languages/code-review-profile-typescript.md` and coding rules in `.agents/rules/languages/coding-rules-typescript.md`.
2. **Execute Static Analysis & Toolchain Verification**:
   - Run: `tsc --noEmit and eslint/biome checks` using `toolchain-typescript`.
   - Confirm zero unhandled warnings or fatal analyzer errors.
3. **Classify by Severity**:
   - Flag issues using `[P0-BLOCKER]`, `[P1-DEFECT]`, or `[P2-MAINTENANCE]`.
   - Provide concrete before/after code snippets for every P0 and P1 finding.
4. **Issue Final Rubric Verdict**:
   - Aggregate evaluation into `code-review-gatekeeper` format.

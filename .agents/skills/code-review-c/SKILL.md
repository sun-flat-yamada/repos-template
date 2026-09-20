---
name: "code-review-c"
description: "Audits C source code diffs against language-specific idioms, memory safety, static analysis, and code-review-profile-c.md."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.c"
  - "**/*.h"
  - "**/Makefile"
  - "**/CMakeLists.txt"
tags:
  - "skill"
  - "code-review"
  - "c"
  - "quality-gate"
---
# Skill: High-Signal Code Review for C (`code-review-c`)

## Instructions
1. **Profile Inspection**:
   - Evaluate all modified `C` files against the high-impact checklist in `.agents/agents/languages/code-review-profile-c.md` and coding rules in `.agents/rules/languages/coding-rules-c.md`.
2. **Execute Static Analysis & Toolchain Verification**:
   - Run: `gcc -Wall -Wextra -Wpedantic -fsanitize=address,undefined and clang-tidy` using `toolchain-c`.
   - Confirm zero unhandled warnings or fatal analyzer errors.
3. **Classify by Severity**:
   - Flag issues using `[P0-BLOCKER]`, `[P1-DEFECT]`, or `[P2-MAINTENANCE]`.
   - Provide concrete before/after code snippets for every P0 and P1 finding.
4. **Issue Final Rubric Verdict**:
   - Aggregate evaluation into `code-review-gatekeeper` format.

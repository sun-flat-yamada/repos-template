---
name: "code-review-cpp"
description: "Audits CPP source code diffs against language-specific idioms, memory safety, static analysis, and code-review-profile-cpp.md."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.cpp"
  - "**/*.hpp"
  - "**/*.cc"
  - "**/*.cxx"
  - "**/*.h"
  - "**/CMakeLists.txt"
tags:
  - "skill"
  - "code-review"
  - "cpp"
  - "quality-gate"
---
# Skill: High-Signal Code Review for CPP (`code-review-cpp`)

## Instructions
1. **Profile Inspection**:
   - Evaluate all modified `CPP` files against the high-impact checklist in `.agents/agents/languages/code-review-profile-cpp.md` and coding rules in `.agents/rules/languages/coding-rules-cpp.md`.
2. **Execute Static Analysis & Toolchain Verification**:
   - Run: `clang-tidy and ctest with address sanitizers` using `toolchain-cpp`.
   - Confirm zero unhandled warnings or fatal analyzer errors.
3. **Classify by Severity**:
   - Flag issues using `[P0-BLOCKER]`, `[P1-DEFECT]`, or `[P2-MAINTENANCE]`.
   - Provide concrete before/after code snippets for every P0 and P1 finding.
4. **Issue Final Rubric Verdict**:
   - Aggregate evaluation into `code-review-gatekeeper` format.

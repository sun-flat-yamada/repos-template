---
name: "code-review-python"
description: "Audits PYTHON source code diffs against language-specific idioms, memory safety, static analysis, and code-review-profile-python.md."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/requirements*.txt"
  - "**/setup.py"
tags:
  - "skill"
  - "code-review"
  - "python"
  - "quality-gate"
---
# Skill: High-Signal Code Review for PYTHON (`code-review-python`)

## Instructions
1. **Profile Inspection**:
   - Evaluate all modified `PYTHON` files against the high-impact checklist in `.agents/agents/languages/code-review-profile-python.md` and coding rules in `.agents/rules/languages/coding-rules-python.md`.
2. **Execute Static Analysis & Toolchain Verification**:
   - Run: `ruff check . and mypy --strict . and pytest` using `toolchain-python`.
   - Confirm zero unhandled warnings or fatal analyzer errors.
3. **Classify by Severity**:
   - Flag issues using `[P0-BLOCKER]`, `[P1-DEFECT]`, or `[P2-MAINTENANCE]`.
   - Provide concrete before/after code snippets for every P0 and P1 finding.
4. **Issue Final Rubric Verdict**:
   - Aggregate evaluation into `code-review-gatekeeper` format.

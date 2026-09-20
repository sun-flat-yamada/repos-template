---
name: "code-review-dart"
description: "Audits DART source code diffs against language-specific idioms, memory safety, static analysis, and code-review-profile-dart.md."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.dart"
  - "**/pubspec.yaml"
  - "**/analysis_options.yaml"
tags:
  - "skill"
  - "code-review"
  - "dart"
  - "quality-gate"
---
# Skill: High-Signal Code Review for DART (`code-review-dart`)

## Instructions
1. **Profile Inspection**:
   - Evaluate all modified `DART` files against the high-impact checklist in `.agents/agents/languages/code-review-profile-dart.md` and coding rules in `.agents/rules/languages/coding-rules-dart.md`.
2. **Execute Static Analysis & Toolchain Verification**:
   - Run: `dart analyze --fatal-infos and dart test` using `toolchain-dart`.
   - Confirm zero unhandled warnings or fatal analyzer errors.
3. **Classify by Severity**:
   - Flag issues using `[P0-BLOCKER]`, `[P1-DEFECT]`, or `[P2-MAINTENANCE]`.
   - Provide concrete before/after code snippets for every P0 and P1 finding.
4. **Issue Final Rubric Verdict**:
   - Aggregate evaluation into `code-review-gatekeeper` format.

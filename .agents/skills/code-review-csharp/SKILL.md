---
name: "code-review-csharp"
description: "Audits CSHARP source code diffs against language-specific idioms, memory safety, static analysis, and code-review-profile-csharp.md."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.cs"
  - "**/*.csproj"
  - "**/*.sln"
tags:
  - "skill"
  - "code-review"
  - "csharp"
  - "quality-gate"
---
# Skill: High-Signal Code Review for CSHARP (`code-review-csharp`)

## Instructions
1. **Profile Inspection**:
   - Evaluate all modified `CSHARP` files against the high-impact checklist in `.agents/agents/languages/code-review-profile-csharp.md` and coding rules in `.agents/rules/languages/coding-rules-csharp.md`.
2. **Execute Static Analysis & Toolchain Verification**:
   - Run: `dotnet format --verify-no-changes and dotnet test` using `toolchain-csharp`.
   - Confirm zero unhandled warnings or fatal analyzer errors.
3. **Classify by Severity**:
   - Flag issues using `[P0-BLOCKER]`, `[P1-DEFECT]`, or `[P2-MAINTENANCE]`.
   - Provide concrete before/after code snippets for every P0 and P1 finding.
4. **Issue Final Rubric Verdict**:
   - Aggregate evaluation into `code-review-gatekeeper` format.

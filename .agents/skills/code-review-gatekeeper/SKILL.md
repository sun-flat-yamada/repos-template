---
name: "code-review-gatekeeper"
description: "Evaluates pull requests and proposed code diffs against the 100-point rubric defined in code-review.agent.md, issuing verdicts and actionable remediation steps."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*"
tags:
  - "skill"
  - "code-review"
  - "gatekeeper"
  - "rubric"
  - "quality-gate"
---
# Skill: Code Review Gatekeeper (`code-review-gatekeeper`)

## Instructions
1. **Scope Inspection**:
   - Inspect modified files and commit diffs (`git diff main...HEAD`).
2. **Execute High-Signal Rubric Audit**:
   - Evaluate the 5 core dimensions:
     1. **Functional Correctness & Spec** (25 pts): Fulfills requirements with zero regression. Deduct 10 pts for missing boundary handling (empty, max, null).
     2. **Test Rigor & Failure Modes** (25 pts): Deduct 15 pts for "shallow tests" (only testing trivial happy paths without error/cancellation tests).
     3. **Security & Secret Defense** (20 pts): Any detected secret or prompt injection vector results in immediate **0/20 & BLOCK**.
     4. **Architectural Cleanliness** (15 pts): Layer boundaries respected; zero hidden side effects.
     5. **Idiomatic Style & Language Profiles** (15 pts): Evaluated strictly against `.agents/agents/languages/code-review-profile-<lang>.md`.
3. **Issue Verdict & Actionable Remediation**:
   - Categorize issues by **`[P0-BLOCKER]`**, **`[P1-DEFECT]`**, **`[P2-MAINTENANCE]`**.
   - Every P0/P1 issue MUST include a concrete code snippet showing the fix.

## Output Format
```markdown
### 🛡️ Code Review Evaluation Report

- **Overall Score**: [XX / 100]
- **Verdict**: [PASS (>=80) | NEEDS WORK (<80) | BLOCK (Security/P0)]

#### Findings & Actionable Remediation
- **[P0-BLOCKER]** `src/api.py:34`: Direct string formatting in SQL query.
  *Remediation*: Use parameterized queries.
- **[P1-DEFECT]** `src/service.ts:89`: Unhandled floating promise in error callback.
  *Remediation*: Add `await` or `void ... .catch()`.
```

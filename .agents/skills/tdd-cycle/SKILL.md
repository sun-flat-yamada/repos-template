---
name: "tdd-cycle"
description: "Drives the Test-Driven Development (TDD) Red-Green-Refactor execution cycle. Formulates failing unit tests first, implements minimal passing logic, and refactors cleanly."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*test*"
  - "**/*_test.*"
  - "**/*.spec.*"
  - "**/*Test.*"
tags:
  - "skill"
  - "tdd"
  - "testing"
  - "unit-test"
  - "quality-gate"
---
# Skill: TDD Cycle (`tdd-cycle`)

## Instructions
1. **Red Phase (Multi-Vector Failing Tests)**:
   - Do NOT write only a single happy-path test. A complete Red phase requires testing:
     1. **Happy Path**: Expected nominal input produces correct output.
     2. **Edge / Boundary**: Empty collections, zero, negative bounds, maximum allowed capacity.
     3. **Failure Mode**: Network timeout, malformed payload, or invalid state throws domain exception.
   - Run the test suite using `toolchain-<lang>` and confirm tests fail for the exact intended assertions.
2. **Green Phase (Minimal & Resilient Implementation)**:
   - Write the cleanest minimal code to satisfy all test cases.
   - Do not write speculative extra features without corresponding tests.
3. **Refactor Phase (Anti-Drift Polish)**:
   - Check against `.agents/rules/coding-rules-general.md` and `.agents/agents/languages/coding-profile-<lang>.md`.
   - Remove duplicate code, ensure proper variable naming, and confirm all tests still pass.

## Best Practices
- Every bug fix MUST begin with a failing reproduction test capturing the defect.
- Tests must be completely deterministic and run without external internet dependencies.

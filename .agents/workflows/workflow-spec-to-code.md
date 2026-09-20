---
title: "Workflow: Spec-to-Code Implementation"
description: "Structured implementation lifecycle from requirements elaboration, design plan, TDD red-green cycle, to review."
category: "workflow"
type: "sop"
status: "active"
date: 2026-09-20
updated: 2026-09-21
lang: "en"
tags:
  - "workflow"
  - "spec-to-code"
  - "tdd"
  - "implementation"
---

# Standard Operating Procedure: Spec to Code (`workflow-spec-to-code`)

This SOP outlines the end-to-end workflow for transforming human user requirements or GitHub Issues into verified production code.

---

## Phase 1: Clarification & Architecture Alignment
1. **Analyze Requirements**: Parse business intent, user constraints, and non-functional requirements.
2. **Check ADRs**: Review `docs/adr/` to ensure proposed solution adheres to existing architecture decisions.
3. **Draft Plan**: If changes involve multi-file architectural shifts, document the plan and obtain user approval.

---

## Phase 2: Test-Driven Development (TDD)
1. **Red Phase**: Write unit or integration tests verifying acceptance criteria using the target language toolchain skill (`.agents/skills/languages/`).
2. **Confirm Failure**: Execute test runner and verify it fails with the expected assertion error.

---

## Phase 3: Implementation & Green Phase
1. **Synthesize Code**: Implement the minimal required logic according to `.agents/rules/coding-rules-general.md` and specific language rules (`.agents/rules/languages/`).
2. **Confirm Pass**: Re-run the test suite until all assertions pass cleanly.

---

## Phase 4: Quality & Security Review Gate
1. **Self-Review**: Run `code-review-gatekeeper` to evaluate the 100-point rubric.
2. **Secret Scan**: Run `security-secret-audit` to guarantee zero token leakage.
3. **Format & Lint**: Run language-specific linters and formatters.

---

## Phase 5: Commit & Pull Request
1. Stage modified files explicitly.
2. Commit with Conventional Commits (`feat:`, `fix:`, etc.).
3. Open a Pull Request following `.github/PULL_REQUEST_TEMPLATE.md`.

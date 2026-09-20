---
name: "adr-management"
description: "Guides the creation, numbering, and status lifecycle management of Architectural Decision Records (ADRs) in docs/adr/."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "docs/adr/**/*.md"
tags:
  - "skill"
  - "adr"
  - "architecture"
  - "decision-record"
---
# Skill: ADR Management (`adr-management`)

## Instructions
1. **Determine Need for ADR**:
   - Create an ADR when choosing a foundational library, altering domain boundaries, switching runtime environments, or introducing cross-cutting design patterns.
2. **Assign Sequential ID**:
   - Check `docs/adr/` for the highest existing sequential number and increment by 1 (e.g. `0001-title.md`).
3. **Draft Document**:
   - Copy `docs/adr/template.md` to `docs/adr/<NNNN>-<kebab-case-title>.md`.
   - Fill in: Status (`Proposed` or `Accepted`), Context, Decision, and positive/negative Consequences.
4. **Link & Commit**:
   - Reference the new ADR in pull request descriptions.
   - If an existing ADR is superseded, update its status to `Superseded by [ADR-XXXX](XXXX-title.md)`.

## Output Example
```markdown
# 1. Adopt Zod for Runtime Validation

Date: 2026-09-20

## Status
Accepted

## Context
TypeScript types vanish at runtime; untrusted API inputs require strict boundary validation.

## Decision
We adopt Zod across all input handlers.

## Consequences
- Safe type-narrowing at API boundaries.
- Small bundle size addition.
```

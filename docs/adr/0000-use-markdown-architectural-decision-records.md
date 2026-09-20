---
title: "ADR-0000: Record Architecture Decisions"
description: "Adoption of Michael Nygard-style Markdown Architectural Decision Records (ADRs) to track key engineering choices."
category: "adr"
type: "decision-record"
status: "accepted"
date: "{CURRENT_YEAR}-09-20"
updated: 2026-09-21
lang: "en"
tags:
  - "adr"
  - "architecture"
  - "decision-record"
  - "governance"
---

# 0. Record Architecture Decisions

Date: {CURRENT_YEAR}-09-20

## Status

Accepted

## Context

We need to record architectural, structural, and tooling decisions made on **{PROJECT_NAME}**. Architectural Decision Records (ADRs) provide transparent rationale for past decisions and guide future engineering choices.

## Decision

We will use Markdown Architectural Decision Records stored in `docs/adr/`. Each ADR will record:
- Title and sequential number
- Date and status (Proposed, Accepted, Deprecated, Superseded)
- Context & problem statement
- Decision & rationale
- Consequences (positive and negative trade-offs)

## Consequences

- Architectural decisions will be tracked in version control alongside code.
- Developers and autonomous AI agents will be able to inspect ADRs before suggesting breaking structural refactorings.
- All team members share visibility into technical trade-offs.

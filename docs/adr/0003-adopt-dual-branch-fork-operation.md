---
title: "ADR-0003: Adopt Dual-Branch Operation for Forks of the Template"
description: "Decision to keep main as a pure upstream mirror and collect all fork-specific changes on fork/custom, with protected-branch pushes left to humans."
category: "adr"
type: "decision-record"
status: "proposed"
date: 2026-10-03
updated: 2026-10-03
lang: "en"
tags:
  - "adr"
  - "fork"
  - "upstream-sync"
  - "git"
---

# 3. Adopt Dual-Branch Operation for Forks of the Template

Date: 2026-10-03

## Status

Proposed. Requires human review (C-HITL-05: `.agents/`, `.github/`, `CLAUDE.md`).

## Context

Forks of this template need to keep receiving upstream improvements while carrying their own customizations. Merging upstream into a branch that also holds fork changes, with `main` as that branch, makes `main` diverge and turns every sync into a conflict risk. The permission policy also forbids agents from pushing `main` (N-08) and from `reset --hard` (C-HITL-03) or force pushes (N-05), so a "reset main to upstream" style sync cannot be automated.

## Decision

- `main` is a pure mirror of `upstream/main`, updated only with `git merge --ff-only`. A divergent `main` is a defect to report, never to fix with a reset.
- All fork-specific changes live on `fork/custom`, the fork's default branch. Upstream changes arrive by merging `main` into it.
- Updating `origin/main` is a documented human step. The policy is not relaxed.
- Zero-code customization (`template.config.yaml`, repository Variables and Secrets) is preferred over code changes, to keep the `fork/custom` delta small.
- `scripts/verify-fork-health.py` is the read-only check of this model. The agent and skill are `fork-sync.agent.md` and `fork-sync-ops`.

## Consequences

### Positive
- Syncing never rewrites history, and conflicts appear only on `fork/custom`.
- Every step is expressible within the existing tiers; no rule IDs change.

### Negative & Trade-offs
- A human must push `main` after each sync.
- Two branches to understand; template CI must also run on `fork/custom` (see the guide).
- This guide does not cover the upstream-sync tooling planned in PR #12; reconcile the two once it lands.

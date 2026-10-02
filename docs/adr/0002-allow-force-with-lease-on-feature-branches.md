---
title: "ADR-0002: Conditionally Allow Explicit --force-with-lease on Feature Branches"
description: "Decision to move a narrowly specified git push --force-with-lease form from N-05 (never) to C-HITL-01 (per-action approval), keeping every other force push denied."
category: "adr"
type: "decision-record"
status: "proposed"
date: 2026-10-02
updated: 2026-10-02
lang: "en"
tags:
  - "adr"
  - "security"
  - "permissions"
  - "ai-agents"
---

# 2. Conditionally Allow Explicit --force-with-lease on Feature Branches

Date: 2026-10-02

## Status

Proposed. Refines [ADR-0001](0001-adopt-ai-agent-permission-policy.md); requires human review (C-HITL-05).

## Context

N-05 denied every force push, including `--force-with-lease`. That forces a "merge base into the branch" workflow once a branch is pushed, and combined with Rebase & Merge it leaves merge commits on feature branches. On the other hand, an unconditional lease is unsafe: a lease only checks that the remote-tracking ref still equals what the local clone last saw. In this repository several agents and IDEs share one clone, and a background `git fetch` by another actor advances the tracking ref, so a lease can succeed and overwrite commits nobody reviewed.

## Decision

Only this form is C-HITL-01 (ask, one-time approval):

`git push --force-with-lease=<branch>:<sha> --force-if-includes <remote> <branch>`

- `<sha>` is mandatory and pins the expected remote tip, which removes the dependence on the tracking ref. The approver verifies it.
- `--force-if-includes` is mandatory; it additionally refuses the push when the local branch does not contain the remote tip.
- The push must name exactly one bare refspec equal to the lease branch (no `+`, `:`, or extra refs) and the branch must not be protected.
- A bare lease, a lease without `<sha>`, a lease without `--force-if-includes`, `--force`, `-f`, `+ref`, `--mirror`, `--prune`, `--delete`, and `:ref` remain N-05. Protected branches remain N-08, with or without a lease.
- The guard (`.claude/hooks/permission-guard.py`) validates the sha format and these conditions; a mismatch is denied. Rule IDs are unchanged.
- Tools that cannot express the condition keep denying every lease form (the stricter side, per ADR-0001): Codex (prefix rules, no flag-position matching), Gemini (policy regex), and Cursor (no ask list). Claude Code's static `deny` rules were narrowed from `--force*` so they no longer match `--force-with-lease`; the PreToolUse hook enforces the lease conditions in all modes. VS Code already requires approval for every push.

## Consequences

### Positive
- Rebased feature branches can be pushed without merge commits, behind a per-action human approval.
- The remaining overwrite risk is bounded by the pinned sha and `--force-if-includes`.

### Negative & Trade-offs
- Only Claude Code can use the new form; other tools stay stricter than the policy.
- The approver must check the sha against the remote; the guard can validate its shape but not its truth.

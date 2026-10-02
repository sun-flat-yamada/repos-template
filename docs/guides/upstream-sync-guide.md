---
title: "Upstream Sync Guide"
description: "How files adopted from github-copilot-dashboard (change-dev agent, skill, rule, worktree script) are tracked and how to pull in upstream updates periodically."
category: "guide"
type: "how-to"
status: "active"
date: 2026-10-02
updated: 2026-10-02
lang: "en"
tags:
  - "upstream"
  - "sync"
  - "change-dev"
  - "maintenance"
---

# Upstream Sync Guide

Some files here are adapted from [`sun-flat-yamada/github-copilot-dashboard`](https://github.com/sun-flat-yamada/github-copilot-dashboard). That repository keeps changing, so this repository tracks what was adopted and when.

## What Is Tracked

Manifest: `.agents/upstream/github-copilot-dashboard.json`

| Upstream file | Adapted file in this repository |
| :--- | :--- |
| `.agents/change-dev.agent.md` | `.agents/agents/change-dev.agent.md` |
| `.agents/skills/change-dev/SKILL.md` | `.agents/skills/change-dev/SKILL.md` |
| `.agents/rules/development-workflow.md` | `.agents/rules/workflow-rules-development.md` |
| `scripts/worktree-manage.ts` | `scripts/worktree-manage.py` (Python port) |

`.agents/upstream/github-copilot-dashboard/` holds **verbatim snapshots** of the upstream files as of `synced_commit`. The adapted files are hand-maintained derivatives and are never overwritten automatically.

Not adopted on purpose:
- `fork-sync-ops`, `benchmark-ingestion`, `preset-curator`, `radar-version-manager`, `sns-buzz-harvester` and the other dashboard agents: project-specific.
- `skills/*` (distribution copies of the same skills) and `secret-guard` (covered by `security-secret-audit`).
- `--force-with-lease`, `worktree remove --force`, and manual directory deletion: they conflict with N-05 / C-HITL-03 in `permission-rules-general.md`.

Local divergences from upstream:
- Auto-Pilot is adopted as-is, but `CHG_DEV_AUTO_PILOT` is **disabled by default** (`.env.example` sets `false`; upstream sets `true`). Its approve / merge steps stay denied by the permission guard (N-08).

## Periodic Update Procedure

1. Check for drift (writes nothing; exit code 1 when upstream changed):
   ```bash
   python scripts/sync-upstream.py check
   ```
2. Refresh the snapshots and read the diffs (`git clone` needs approval, C-HITL-01):
   ```bash
   python scripts/sync-upstream.py update
   ```
3. Port each reported diff into its adapted file, keeping the local divergences listed above and the repository's naming, front-matter, language, and permission rules.
4. Run the validators and tests (see CI), then open a PR titled like `chore(upstream): sync github-copilot-dashboard <short-sha>` with the commit range in the description.

To track more upstream files, add `{"source": ..., "adapted": ...}` entries to the manifest and run `update`. To track another upstream repository, add a second manifest next to the first (the snapshot directory is named after the manifest file).

`.github/workflows/upstream-sync-check.yml` runs `check` weekly and fails when upstream has moved, which is the reminder to run this procedure.

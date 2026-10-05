---
title: "Upstream Sync Guide"
description: "How files adopted from related repositories (github-copilot-dashboard, claude-audit-dashboard) are tracked per manifest and how to pull in upstream updates periodically."
category: "guide"
type: "how-to"
status: "active"
date: 2026-10-02
updated: 2026-10-05
lang: "en"
tags:
  - "upstream"
  - "sync"
  - "change-dev"
  - "maintenance"
---

# Upstream Sync Guide

Some files here are adapted from related repositories. Those repositories keep changing, so this repository tracks what was adopted and when, with one manifest per upstream repository in `.agents/upstream/`. [`sun-flat-yamada/github-copilot-dashboard`](https://github.com/sun-flat-yamada/github-copilot-dashboard) is the canonical upstream for the `change-dev` files.

> Not to be confused with [`fork-operations-guide.md`](fork-operations-guide.md): that guide covers a fork following **this template** (`main` mirror + `fork/custom`). This guide covers **this template** following its reference repository `github-copilot-dashboard`. The tracked files and procedures are separate.

## What Is Tracked

Manifest: `.agents/upstream/github-copilot-dashboard.json`

| Upstream file | Adapted file in this repository |
| :--- | :--- |
| `.agents/change-dev.agent.md` | `.agents/agents/change-dev.agent.md` |
| `.agents/skills/change-dev/SKILL.md` | `.agents/skills/change-dev/SKILL.md` |
| `.agents/rules/development-workflow.md` | `.agents/rules/workflow-rules-development.md` |
| `scripts/worktree-manage.ts` | `scripts/worktree-manage.py` (Python port) |

Manifest: `.agents/upstream/claude-audit-dashboard.json` ([`sun-flat-yamada/claude-audit-dashboard`](https://github.com/sun-flat-yamada/claude-audit-dashboard))

| Upstream file | Adapted file in this repository |
| :--- | :--- |
| `.agents/rules/naming-rules-general.md` | `.agents/rules/naming-rules-general.md` (front-matter convention with `alwaysApply`, not ported yet) |

`.agents/upstream/<manifest name>/` holds **verbatim snapshots** of the upstream files as of that manifest's `synced_commit`. The adapted files are hand-maintained derivatives and are never overwritten automatically.

Not adopted on purpose:
- `fork-sync-ops`, `benchmark-ingestion`, `preset-curator`, `radar-version-manager`, `sns-buzz-harvester` and the other dashboard agents: project-specific.
- `skills/*` (distribution copies of the same skills) and `secret-guard` (covered by `security-secret-audit`).
- `worktree remove --force` and manual directory deletion: they conflict with C-HITL-03 in `permission-rules-general.md`.

Local divergences from upstream:
- Upstream pushes with a plain `--force-with-lease`. Here only `git push --force-with-lease=<branch>:<sha> --force-if-includes origin <branch>` is allowed, as a C-HITL-01 approval on a non-protected feature branch (ADR-0002); a bare lease, a lease without `<sha>` or `--force-if-includes`, `--force`, and `-f` stay denied (N-05).
- Auto-Pilot is adopted as-is, but `CHG_DEV_AUTO_PILOT` is **disabled by default** (`.env.example` sets `false`; upstream sets `true`). Its approve / merge steps stay denied by the permission guard (N-08).

## Periodic Update Procedure

1. Check every manifest for drift (writes nothing; exit code 1 when an upstream changed, 2 when a manifest could not be processed, for example an unreachable repository; the other manifests are still checked):
   ```bash
   python scripts/sync-upstream.py check
   ```
2. Refresh the snapshots of one upstream and read the diffs (`git clone` needs approval, C-HITL-01). Use `--manifest` so that snapshots of other upstreams are not refreshed before their diffs are ported:
   ```bash
   python scripts/sync-upstream.py update --manifest .agents/upstream/github-copilot-dashboard.json
   ```
3. Port each reported diff into its adapted file, keeping the local divergences listed above and the repository's naming, front-matter, language, and permission rules.
4. Run the validators and tests (see CI), then open a PR titled like `chore(upstream): sync github-copilot-dashboard <short-sha>` with the commit range in the description.

To track more upstream files, add `{"source": ..., "adapted": ...}` entries to the manifest and run `update`. To track another upstream repository, add a manifest next to the others and run `update --manifest <it>` once; `check` picks it up automatically (the snapshot directory is named after the manifest file).

`.github/workflows/upstream-sync-check.yml` runs `check` over all manifests weekly and fails when an upstream has moved, which is the reminder to run this procedure.

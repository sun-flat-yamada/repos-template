---
title: "Development Workflow & Multi-Agent Worktree Rules"
description: "Mandatory change lifecycle for AI agents and humans: Issue, plan gate, sibling worktree, quality gate, PR, human-gated rebase merge, and cleanup."
category: "rule"
type: "rule"
status: "active"
date: 2026-10-02
updated: 2026-10-02
lang: "en"
tags:
  - "rules"
  - "workflow"
  - "git-worktree"
  - "multi-agent"
---

# Development Workflow & Multi-Agent Worktree Rules (`workflow-rules-development`)

> Adapted from `sun-flat-yamada/github-copilot-dashboard` (`.agents/rules/development-workflow.md`).
> Tracked by `.agents/upstream/github-copilot-dashboard.json`.

All AI agents (Claude Code, Codex, Gemini / Antigravity, Cursor, Copilot, ...) MUST follow this lifecycle when changing the repository. Permission tiers in `permission-rules-general.md` always win over this document.

## 1. Branch Protection
- Never commit or push directly to `main`, `master`, `trunk`, `release*`, or `production` (N-08).
- Non-trivial changes follow: **Issue → Plan → Sibling Worktree → Quality Gate → PR → Human Rebase & Merge → Cleanup**.

## 2. Sibling Worktree Rule
Concurrent agents must not share a working tree.
1. Do not edit files or run long builds in the primary working tree.
2. Place worktrees beside the repository, never inside it: `../<repo>-worktrees/<branch-slug>` (`<branch-slug>` replaces `/` with `-`).

## 3. Lifecycle

| Step | What | Gate |
| :--- | :--- | :--- |
| 1. Issue | Why / What / Acceptance Criteria | Issue number recorded |
| 2. Plan | `implementation_plan.md` + `task.md` in `.devs/changes/yyyy-mm-dd_<ChangeTitle>/` of the primary root | **Explicit user sign-off** |
| 3. Worktree | `python scripts/worktree-manage.py add <branch>` | Based on latest `origin/<base>` |
| 4. Implement | Tests first (TDD), atomic Conventional Commits, update `docs/` | — |
| 5. Quality gate | See section 4 | All checks exit 0 |
| 6. Walkthrough | `walkthrough.md` with diff summary and gate results | Gate green |
| 7. PR | Rebase (unpushed) or merge base (pushed); push feature branch; open **draft** PR with `Closes #<id>` | C-HITL approval for push / PR |
| 8. Merge | A human merges using **Rebase & Merge** | Never the agent (N-08) |
| 9. Cleanup | `python scripts/worktree-manage.py clean <branch>` from the primary root | After merge |

Plan artifacts are shared via the PR, so they must contain no secrets, PII, or machine-specific absolute paths. Scratch files stay outside the repository.

## 4. Quality Gate
Run inside the worktree; every command must exit 0:
1. `python scripts/validate-filenames.py`
2. `python scripts/validate-frontmatter.py`
3. Repository tests (for example `python tests/test-permission-guard.py`)
4. Language lint / type-check / test / build (see `.agents/skills/toolchain-{PRIMARY_LANGUAGE}/SKILL.md`)
5. Secret scan (`security-secret-audit` skill)

## 5. Absolute Guardrails
- No force-push, no `--no-verify`, no history rewrite of pushed commits.
- Never bypass the quality gate or branch protection.

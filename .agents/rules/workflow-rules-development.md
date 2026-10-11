---
title: "Development Workflow & Multi-Agent Worktree Rules"
description: "Mandatory change lifecycle for AI agents and humans: Issue, plan gate, sibling worktree, quality gate, PR, human-gated rebase merge, and cleanup."
category: "rule"
type: "rule"
status: "active"
date: 2026-10-02
updated: 2026-10-12
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
| 1. Issue | Why / What / Acceptance Criteria; one plan task = one Work-Unit Issue (`.github/ISSUE_TEMPLATE/work-unit.yml`) under a per-phase tracking Issue | Issue number recorded |
| 2. Plan | `implementation_plan.md` + `task.md` in `.devs/changes/yyyy-mm-dd_<ChangeTitle>/` of the primary root, committed on their own before any implementation file is touched | **Explicit user sign-off** |
| 3. Worktree | `python scripts/worktree-manage.py add <branch>` | Based on latest `origin/<base>` |
| 4. Implement | Tests first (TDD), atomic Conventional Commits, update `docs/` | — |
| 5. Quality gate | See section 4 | All checks exit 0 |
| 6. Walkthrough | `walkthrough.md` with diff summary and gate results | Gate green |
| 7. PR | Rebase (unpushed) or merge base (pushed; default). Optionally rebase a pushed branch and push with `--force-with-lease=<branch>:<sha> --force-if-includes` (approval required); push feature branch; open **draft** PR with `Closes #<id>` | C-HITL approval for push / PR |
| 8. Merge | **Rebase & Merge**; manual by default, automatic only with Auto-Pilot (section 6) | Agent-side merge is denied by N-08 unless the policy is changed |
| 9. Cleanup | `python scripts/worktree-manage.py remove <branch>` from the primary root | After merge |

Plan artifacts are shared via the PR, so they must contain no secrets, PII, or machine-specific absolute paths (use repository-relative links, never `file:///`). Scratch files stay outside the repository. The last items of `task.md` are the PR **and** the merge.

A Work-Unit Issue is the hand-off between sessions: a new session starts from "Resolve Issue #N", reads the Issue, its parent and the referenced documents, checks the prerequisites are merged, and opens the PR with `Closes #N`. Findings outside the Issue's scope become new Issues. Details: `change-dev` skill (Work-Unit Issue).

Claude Code cloud sessions (`CLAUDE_CODE_REMOTE=true`) skip steps 3 and 9: the session VM is the isolation unit, and the work happens on the session's branch. See the `change-dev` skill (Claude Code Cloud Sessions).

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
- Never merge with a failed or running check, a merge conflict, or an unanswered review thread.

## 6. Auto-Pilot (`CHG_DEV_AUTO_PILOT`)
Opt-in mode that carries a change from PR creation to Rebase & Merge. Enabled only when `CHG_DEV_AUTO_PILOT` is `true` or `1`; resolution order is process environment → `.env` → `.env.example`. The repository default in `.env.example` is `false` (disabled).
- Never relaxed: the plan **Proceed** gate, branch protection, required reviews. Never use `--admin`; never self-approve. Merge only at the head SHA whose checks passed.
- Recommended repository setting: *Automatically delete head branches* (`delete_branch_on_merge: true`).
- Enforcement: agent-side `gh pr merge` and `gh pr review --approve` are N-08 and denied by `.claude/settings.json` / `permission-guard.py`. Enabling the key does not lift that denial; changing it requires a human-reviewed policy change (ADR + every enforcement file, per `permission-rules-general.md` section 5).

---
name: "change-dev"
description: "Runs the end-to-end change lifecycle with sibling Git worktrees for concurrent AI agents: Issue scoping, plan gate, worktree provisioning, quality gate, walkthrough, rebase-synchronized draft PR, and post-merge cleanup."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*"
tags:
  - "skill"
  - "change-dev"
  - "git-worktree"
  - "workflow"
  - "pull-request"
---
# Skill: Change Dev & Multi-Agent Worktree (`change-dev`)

> Adapted from `sun-flat-yamada/github-copilot-dashboard` (`.agents/skills/change-dev/SKILL.md`).
> Tracked by `.agents/upstream/github-copilot-dashboard.json`.

Use when planning or making code, documentation, or architecture changes, especially when several agents work in parallel. Rules: `.agents/rules/workflow-rules-development.md`. Persona: `.agents/agents/change-dev.agent.md`.

## Before You Start
- Never commit or push to a protected branch (`main`, `master`, `trunk`, `release*`, `production`).
- Never edit in the primary working tree; use a sibling worktree.
- Pushes, `gh` calls, and PR creation need per-action human approval (C-HITL-01).

## Plan Artifacts
One directory per change in the **primary repository root** (not in the worktree):

```text
.devs/changes/yyyy-mm-dd_<ChangeTitle>/
├── implementation_plan.md   # written before any code change; needs user sign-off
├── task.md                  # live checklist
└── walkthrough.md           # written after the quality gate passes
```

- `<ChangeTitle>`: short kebab-case or PascalCase, no spaces or path-unsafe characters.
- Content rules: no secrets, PII, or absolute local paths.
- Google Antigravity: write each file with `ArtifactMetadata` (`UserFacing: true`; `RequestFeedback: true` only for `implementation_plan.md`, which renders the **Proceed** button) and keep a finished copy in the directory above. Never add `ArtifactMetadata` to ordinary repository files.

`implementation_plan.md` sections: context, **User Review Required** (decisions, breaking changes), **Proposed Changes** (`[NEW]` / `[MODIFY]` / `[DELETE]` per file), **Verification Plan**.
`walkthrough.md` sections: summary, changes made, quality gate results table (stage / command / result).

## Phases

1. **Issue** — create or reference an Issue (Why, What, Acceptance Criteria). Record `#<id>`.
2. **Plan gate** — write `implementation_plan.md` and `task.md`; stop until the user signs off.
3. **Worktree**
   ```bash
   python scripts/worktree-manage.py add feat/42-new-feature   # optional 2nd arg: base branch (default: main)
   cd ../<repo>-worktrees/feat-42-new-feature
   ```
   Then run the lockfile-faithful install for the language (see `toolchain-*` skills).
4. **Implement** — tests first, atomic Conventional Commits (English), update `docs/`; keep `task.md` current.
5. **Quality gate** — all must exit 0:
   ```bash
   python scripts/validate-filenames.py
   python scripts/validate-frontmatter.py
   # plus the repository tests and the language lint / type-check / test / build
   ```
6. **Walkthrough** — write `walkthrough.md`; tick every item in `task.md`.
7. **Sync & PR**
   ```bash
   git fetch origin main
   git rebase origin/main      # branch not pushed yet
   git merge origin/main       # branch already pushed: default, keeps pushed history intact
   # Alternative for a pushed branch: git rebase origin/main, then push with an explicit expected sha
   #   git push --force-with-lease=<branch>:<sha> --force-if-includes origin <branch>   (per-action approval, C-HITL-01; the human verifies <sha> against the remote)
   ```
   Re-run the gate after resolving conflicts. Push with approval (`git push -u origin <branch>`), then open a **draft** PR (title: `feat(scope): 日本語の説明`, body in Japanese, `Closes #42`) using the PR template.
8. **Merge** — manual by default: a human performs **Rebase & Merge**. With Auto-Pilot enabled, the agent does it (see below).
9. **Cleanup** — from the primary root: `python scripts/worktree-manage.py remove feat/42-new-feature`, then `git checkout main && git pull --ff-only origin main`.

## Auto-Pilot Mode (`CHG_DEV_AUTO_PILOT`)

Opt-in mode that carries a change from **PR creation to Rebase & Merge completion** without manual intervention.

| Item | Value |
| :--- | :--- |
| Key | `CHG_DEV_AUTO_PILOT` |
| Enabled when | value is `true` (case-insensitive) or `1` |
| Disabled when | unset or any other value |
| Resolution order | process environment → `.env` → `.env.example` |
| Repository default | **disabled** (`CHG_DEV_AUTO_PILOT=false` in `.env.example`) |

Behavior after PR creation:
1. **Wait for CI**: `gh pr checks <id> --watch` until required checks complete.
2. **Self-heal**: on a failing check, fix in the worktree, re-run the quality gate, push, watch again. Never skip or disable tests.
3. **Approval**: request review when required; approve with `gh pr review <id> --approve` only when the authenticated account is not the PR author.
4. **Rebase & Merge**: once CI is green with no conflicts or unresolved threads, `gh pr merge <id> --rebase --delete-branch` (or `--auto --rebase` while checks are pending).
5. **Cleanup**: step 9 above.

Never relaxed: the plan **Proceed** gate; never `--admin`, never bypass branch protection or required reviews, never push to a protected branch.

> [!WARNING]
> Steps 3 and 4 are N-08 in `permission-rules-general.md`. `.claude/settings.json` and `.claude/hooks/permission-guard.py` deny them in every mode, so enabling the key does not lift the denial. Auto-Pilot stops at the denied command and reports; changing that is a human-reviewed policy change (C-HITL-05).

## Stop and Ask When
- Approval from another person is required, a rebase/merge conflict is non-trivial, or checks stay red after a fix.

## Staying Current With Upstream
This skill is a hand-adapted derivative. Updates are pulled with `python scripts/sync-upstream.py check|update` (see `docs/guides/upstream-sync-guide.md`).

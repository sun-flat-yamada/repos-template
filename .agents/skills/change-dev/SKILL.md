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
   git merge origin/main       # branch already pushed: never rewrite pushed history
   ```
   Re-run the gate after resolving conflicts. Push with approval (`git push -u origin <branch>`), then open a **draft** PR (title: `feat(scope): 日本語の説明`, body in Japanese, `Closes #42`) using the PR template.
8. **Merge** — a human performs **Rebase & Merge**. The agent never merges or approves (N-08).
9. **Cleanup** — from the primary root: `python scripts/worktree-manage.py clean feat/42-new-feature`, then `git checkout main && git pull --ff-only origin main`.

## Stop and Ask When
- Approval from another person is required, a rebase/merge conflict is non-trivial, or checks stay red after a fix.
- The upstream `change-dev` Auto-Pilot (agent-side approve/merge) is **not adopted** here because it conflicts with N-08.

## Staying Current With Upstream
This skill is a hand-adapted derivative. Updates are pulled with `python scripts/sync-upstream.py check|update` (see `docs/guides/upstream-sync-guide.md`).

---
title: "ADR-0003: Gate Forced Worktree Removal Behind a Checked Script"
description: "Decision to keep raw git worktree remove --force at C-HITL-03 and allow forced removal only through scripts/worktree-manage.py remove, which refuses unless no work can be lost."
category: "adr"
type: "decision-record"
status: "proposed"
date: 2026-10-03
updated: 2026-10-03
lang: "en"
tags:
  - "adr"
  - "security"
  - "permissions"
  - "ai-agents"
  - "git-worktree"
---

# 3. Gate Forced Worktree Removal Behind a Checked Script

Date: 2026-10-03

## Status

Proposed. Refines [ADR-0001](0001-adopt-ai-agent-permission-policy.md); requires human review (C-HITL-05). Related: [ADR-0002](0002-allow-force-with-lease-on-feature-branches.md).

## Context

Agents work in sibling worktrees (`../<repo>-worktrees/<branch-slug>`) and must remove them after the PR is merged. `git worktree remove` fails on untracked files, modifications, or locks, so cleanup of otherwise finished worktrees needs `--force`. But `--force` also discards uncommitted and unpushed work silently, and several agents and IDEs share one clone. Before this ADR no rule named `git worktree`; every form fell through to the default C-HITL (ask), and the relation to `git clean -f` (C-HITL-03) and to `rm -rf` as a workaround was undocumented.

## Decision

Option (B) of issue #14: the check lives in a script, not in the guard.

1. `python scripts/worktree-manage.py remove <branch>` is the only sanctioned forced removal. It runs `git worktree remove --force` only after ALL of these hold:
   - the target is the sibling worktree directory of that branch, registered in `git worktree list`, and is neither the main worktree nor the current working directory;
   - the worktree has `<branch>` checked out and is not locked;
   - there are no tracked changes (staged or unstaged) and no untracked files other than git-ignored ones;
   - HEAD is contained in `origin/<branch>` or in `origin/main` (pushed, or merged with the remote branch deleted).
   Otherwise it exits with status 2 and lists the reasons; a human decides. The local branch is deleted with `git branch -d` only (kept when unmerged).
2. Raw `git worktree remove|rm|move|mv` with `--force`/`-f` (including `-f -f` and `-ff` for locked worktrees, `git -C`, `bash -c`, `env`) is C-HITL-03, enforced by `permission-guard.py`, and pointed at the script in its message. The guard does NOT inspect git state.
3. Not forced: `git worktree remove` (fails on dirty trees, so nothing is lost), `list`, `add`, and `prune` keep the normal flow (default ask where no sandbox rule applies). `python scripts/worktree-manage.py ...` runs as ordinary project code (C-SBX-01).
4. Rule IDs are unchanged. Tools that cannot express flag positions treat every `git worktree remove|move` as ask (Codex, Gemini, VS Code) or already prompt (Cursor), i.e. stricter than the policy, per ADR-0001.

Rejected: (A) status quo cannot automate cleanup; (C) the guard would need git state and path logic with many bypass spellings; (D) documentation alone has no enforcement.

## Consequences

### Positive
- Agents can clean up finished worktrees without a prompt-free path to discard unpushed work.
- One tested implementation of the safety conditions; tool configs stay simple.

### Negative & Trade-offs
- The script is a trusted code path: whoever can edit it can weaken the check (`scripts/` edits go through PR review, but are not C-HITL-05 paths). It can only be bypassed by running `git` directly, which stays gated.
- The conditions are point-in-time and approximate: a push by another actor between check and removal is not detected, and "pushed" means the local remote-tracking ref is current (the script does not fetch).
- Worktrees whose remote branch is gone and which were never merged into `origin/main` are reported, not removed, even if the work is obsolete.

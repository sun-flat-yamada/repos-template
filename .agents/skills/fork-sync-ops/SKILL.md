---
name: "fork-sync-ops"
description: "Synchronizes a fork of this template with upstream using the dual-branch model (main = upstream mirror, fork/custom = default branch), with human-only steps for protected branches."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - ".github/**/*"
  - "scripts/verify-fork-health.py"
tags:
  - "skill"
  - "fork"
  - "git"
  - "upstream-sync"
  - "workflow"
---
# Skill: Fork Sync Operations (`fork-sync-ops`)

Rationale and background: [`docs/guides/fork-operations-guide.md`](../../../docs/guides/fork-operations-guide.md), [ADR-0003](../../../docs/adr/0003-adopt-dual-branch-fork-operation.md).

## Branch Model
| Branch | Role | Who may update it |
| :--- | :--- | :--- |
| `main` | Pure mirror of `upstream/main`. Never receives fork-only commits. | Human only (N-08). Fast-forward only. |
| `fork/custom` | Fork default branch. Holds all fork-specific changes. | Agent or human via normal commits and merges. |

## Instructions
1. **Preflight**
   - `python scripts/verify-fork-health.py`. A missing `upstream` remote is fixed by a human-approved `git remote add upstream <template-url>` (C-HITL-01).
2. **Fetch** (C-HITL-01 network): `git fetch upstream`.
3. **Refresh the mirror locally**
   - `git switch main`, then `git merge --ff-only upstream/main`.
   - If this fails, `main` holds fork-only commits. Stop and report; do not reset.
4. **Merge into the customization branch**
   - `git switch fork/custom`, then `git merge main`.
   - Resolve conflicts as in the agent directives; regenerate lockfiles with the repo tooling.
5. **Quality gate** (same as CI, see `.github/workflows/ci.yml`):
   ```bash
   python scripts/validate-filenames.py
   python scripts/validate-frontmatter.py
   python tests/test-validate-frontmatter.py -v
   python tests/test-permission-guard.py -v
   python tests/test-verify-fork-health.py -v
   ```
6. **Push the customization branch** (C-HITL-01 / C-SCOPE-02, per-action approval): `git push -u origin fork/custom`.
7. **Hand off the mirror update to a human** (N-08). Provide, do not run: `git push origin main`.
8. **Final check**: `python scripts/verify-fork-health.py` should report no `FAIL`.

## Keeping the Fork Identifiable
- Fork-specific values (name, owner, URLs) live in `template.config.yaml`, applied with `python scripts/apply-template.py` on `fork/custom` only.
- Never edit upstream-owned files on `main`. Put overrides on `fork/custom` and keep them small to limit conflicts.

## Contributing Back to Upstream
Before opening an upstream PR from a fork change, create a topic branch from `upstream/main` (not `fork/custom`) and cherry-pick only the generic commits. Verify with `git diff upstream/main --stat` that no fork identifiers, secrets, or fork-only paths are included, and that no `template.config.yaml` values leaked.

## Policy Map
| Operation | Rule |
| :--- | :--- |
| `git fetch upstream`, `git remote add upstream` | C-HITL-01 / C-HITL-04 |
| `git merge --ff-only`, `git merge main` (local) | C-SBX-03 |
| `git push origin fork/custom` | C-HITL-01, C-SCOPE-02 |
| `git push origin main` | N-08, human only |
| `git reset --hard`, force push | C-HITL-03 / N-05, not used |
| `gh workflow disable/enable` | C-HITL-01, human-approved |

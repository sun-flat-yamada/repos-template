---
name: "git-workflow"
description: "Executes standard Git workflow operations including branch creation, Conventional Commits formatting, pre-commit validation, and pull request hygiene."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - ".github/**/*"
  - ".githooks/**/*"
  - "**/*"
tags:
  - "skill"
  - "git"
  - "workflow"
  - "vcs"
  - "conventional-commits"
---
# Skill: Git Workflow (`git-workflow`)

## Instructions
1. **Branch Verification**:
   - Check current git branch and status before making modifications (`git status`, `git branch --show-current`).
   - If currently on `main`, create a topic branch using conventional prefixes (`feat/`, `fix/`, `docs/`, `refactor/`, `chore/`).
2. **Pre-Commit Checks**:
   - Run verification scripts before staging:
     ```bash
     python scripts/apply-template.py --check
     ```
3. **Commit Formatting**:
   - Format commit messages strictly to the Conventional Commits specification:
     `type(scope): subject`
   - Keep the first line under 72 characters.
4. **Staging & Commit**:
   - Stage specific files explicitly rather than running `git add .` indiscriminately.
   - Verify that no secret files (`.env`, `*.pem`, `id_rsa`) are staged.

## Examples
```bash
# Good Branch & Commit
git checkout -b feat/oauth-auth-handler
git add src/auth/oauth.py tests/test_oauth.py
git commit -m "feat(auth): implement OAuth2 token refresh handler"
```

## Best Practices
- Never use `--no-verify` to bypass Git hooks.
- Keep commits atomic: one conceptual change per commit.

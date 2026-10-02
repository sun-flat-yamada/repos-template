---
title: Git Commit & Branch Rules
description: Conventional Commits specification, branch naming standards, and pre-commit
  verification workflows.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-10-03
lang: en
tags:
- rules
- git
- commits
- branching
- workflow
alwaysApply: false
globs:
- .git/**/*
- '**/*'
---
# Git Commit & Branching Rules (`git-rules-commit`)

All git operations must follow these conventions to ensure an auditable and automated repository lifecycle.

## 1. Conventional Commits Specification
Commit messages must follow the structure:
```text
<type>(<optional-scope>): <short imperative description>

[optional body explaining motivation and trade-offs]

[optional footer(s), e.g. Closes #123, BREAKING CHANGE: ...]
```

### Allowed Types
- `feat`: New feature or user-facing capability.
- `fix`: Bug fix.
- `docs`: Documentation only changes.
- `style`: Formatting, missing semicolons, white-space changes (no code behavior change).
- `refactor`: Code changes that neither fix a bug nor add a feature.
- `perf`: Performance improvement.
- `test`: Adding or correcting tests.
- `build`: Changes affecting build system or external dependencies.
- `ci`: Changes to CI configuration files and scripts.
- `chore`: Maintenance tasks, repo tooling, housekeeping.
- `revert`: Reverting a previous commit.

## 2. Branch Naming Standards
- `feat/<short-description>`: New features.
- `fix/<short-description>`: Bug fixes.
- `docs/<short-description>`: Documentation changes.
- `refactor/<short-description>`: Code restructuring.
- `chore/<short-description>`: Routine updates.

## 3. Language of Commits and Pull Requests
- Commit messages: English, following the Conventional Commits structure above.
- Pull request titles: keep the Conventional Commits `<type>(<optional-scope>):` prefix in English; write the description after the colon in Japanese (e.g. `feat(auth): ログイン失敗時のリトライを追加`). The `pr-hygiene` workflow validates only the type prefix.
- Pull request descriptions (including the filled-in `.github/PULL_REQUEST_TEMPLATE.md`): Japanese. Keep technical terms, identifiers, and error messages in their original English.

See [`docs/guides/language-policy-guide.md`](../../docs/guides/language-policy-guide.md) for the full language policy, per-tool settings, and how to switch commit messages to Japanese.

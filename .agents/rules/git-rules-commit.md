---
title: Git Commit & Branch Rules
description: Conventional Commits specification, branch naming standards, and pre-commit
  verification workflows.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
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

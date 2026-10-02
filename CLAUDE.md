---
title: "Claude Code Configuration for {PROJECT_NAME}"
description: "Context rules, command shortcuts, and operational directives for Claude Code and AI assistant workflows."
category: "meta"
type: "configuration"
status: "active"
date: 2026-09-20
updated: 2026-10-03
lang: "en"
tags:
  - "claude-code"
  - "ai"
  - "agent"
  - "configuration"
---

# Claude Code Configuration for {PROJECT_NAME}

## Global Rules & Context
@.agents/rules/coding-rules-general.md
@.agents/rules/naming-rules-general.md
@.agents/rules/security-rules-general.md
@.agents/rules/git-rules-commit.md
@.agents/rules/permission-rules-general.md

## Commands
- `/status`: Show git status, current branch, and template placeholder verification.
- `/apply-template`: Run `python scripts/apply-template.py` to substitute project parameters.
- `/test`: Run automated test suites corresponding to `{PRIMARY_LANGUAGE}`.
- `/check-names`: Run `python scripts/validate-filenames.py` to verify file naming rules.
- `/review`: Evaluate current branch against `.agents/agents/code-review.agent.md`.
- `/change-dev`: Follow `.agents/skills/change-dev/SKILL.md` (Issue → plan gate → sibling worktree → quality gate → draft PR).
- `/sync-upstream`: Run `python scripts/sync-upstream.py check` (then `update`) per `docs/guides/upstream-sync-guide.md`.
- `/verify-fork`: In a fork, run `python scripts/verify-fork-health.py` and follow `.agents/skills/fork-sync-ops/SKILL.md` / `docs/guides/fork-operations-guide.md` (never push `main`).
- `/plan`: Create an implementation plan before writing or refactoring significant code.

## Directives
- **Naming Rule Enforcement**: Adhere strictly to `.agents/rules/naming-rules-general.md`. Agent definition files MUST use the suffix `*.agent.md` and MUST NEVER use the `agent-` prefix.
- **Zero Secrets**: Never output or commit API keys, tokens, or private credentials.
- **Permission Tiers**: Follow `.agents/rules/permission-rules-general.md` (A: always allow, C: conditional, N: never). `.claude/settings.json` and `.claude/hooks/permission-guard.py` enforce it; never try to work around a denied or prompted action.
- **TDD Requirement**: Propose unit tests before modifying or implementing application logic.
- **Output Language**: Reply to the user and write PR titles/descriptions in Japanese; commit messages, code, identifiers, and comments stay in English. Details: `.agents/rules/git-rules-commit.md`.
- **Language Alignment**: Consult language-specific profile in `.agents/agents/languages/coding-profile-{PRIMARY_LANGUAGE}.md`.

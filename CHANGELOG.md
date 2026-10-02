---
title: "Changelog"
description: "Chronological history of notable additions, modifications, and deprecations adhering to Keep a Changelog and Semantic Versioning."
category: "governance"
type: "changelog"
status: "active"
date: 2026-09-20
updated: 2026-10-02
lang: "en"
tags:
  - "changelog"
  - "release"
  - "versioning"
---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Standardized GitHub repository template scaffold with automated placeholder substitution.
- Multi-layer AI Agent system architecture supporting 9 major languages (C, C++, C#, TS, JS, Dart, Go, Rust, Python).
- 2026 Open Standard `SKILL.md` packages for Git workflow, TDD cycle, ADR management, and code reviews.
- 4-layer defense-in-depth security model with Gitleaks and pre-commit hooks.
- GitHub Actions CI/CD workflows for testing, hygiene, secret scanning, and automated releases.
- Three-tier AI agent permission policy (`.agents/rules/permission-rules-general.md`: always allow, conditionally allow by condition, never allow) with ADR-0001 and a research guide (`docs/guides/ai-permission-guide.md`).
- Permission configurations for Claude Code (`.claude/settings.json`), Codex CLI (`.codex/`), Gemini CLI (`.gemini/settings.json`, `.gemini/policies/`), Cursor (`.cursor/`), and GitHub Copilot in VS Code (`.vscode/settings.json`).
- PreToolUse guard hook (`.claude/hooks/permission-guard.py`) with unit and configuration-invariant tests run in CI.
- Repository review and improvement plan (`docs/plans/template-improvement-plan.md`) with the maintainers' decisions, and an ADR-0001 addendum on Claude Code auto mode and the unsandboxed retry.
- Unit tests for `scripts/validate-frontmatter.py`; CI now runs the front-matter validator and its tests.

### Changed
- `.gitignore` now tracks the shared `.claude/settings.json` and `.claude/hooks/` while keeping personal Claude Code files local.
- `template.config.yaml` is the only template configuration file; `template.config.json` was removed.
- Every GitHub Actions workflow declares least-privilege `permissions:`.
- Files whose format GitHub or an AI tool owns (the pull request template, READMEs, `CLAUDE.md`, and others) may omit front matter.

### Fixed
- `.gitignore` no longer ignores Dart `lib/` and `bin/`, Go `pkg/`, a root `Makefile`, `Testing/` at any depth, `Cargo.lock`, or `pubspec.lock`, and it now tracks `.claude/skills/`, `.claude/agents/`, and `.claude/commands/`.
- The pull request template no longer copies a YAML front-matter block into every pull request body.
- The guard and every tool's permission configuration now block `git config` changes to `core.hooksPath` (N-04) and publishing through runners such as `uv run`, `uvx`, `npx`, and `python -m` (N-10).
- Documentation no longer refers to a nonexistent `make check`, Windsurf support through `.cursorrules`, or `.agents/skills/languages/`; branch examples use `feat/`; a nested code fence in `code-review.agent.md` renders correctly; the `trailing-whitespace` hook keeps Markdown hard line breaks.

## [1.0.0] - {CURRENT_YEAR}-09-20

### Added
- Initial release of `{PROJECT_NAME}` template.

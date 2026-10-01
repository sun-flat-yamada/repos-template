---
title: "Changelog"
description: "Chronological history of notable additions, modifications, and deprecations adhering to Keep a Changelog and Semantic Versioning."
category: "governance"
type: "changelog"
status: "active"
date: 2026-09-20
updated: 2026-10-01
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

### Changed
- `.gitignore` now tracks the shared `.claude/settings.json` and `.claude/hooks/` while keeping personal Claude Code files local.

## [1.0.0] - {CURRENT_YEAR}-09-20

### Added
- Initial release of `{PROJECT_NAME}` template.

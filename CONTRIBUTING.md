---
title: "Contributing to {PROJECT_NAME}"
description: "Guidelines and instructions for contributing to the project, covering branch management, commit conventions, and pull request workflows."
category: "governance"
type: "guidelines"
status: "active"
date: 2026-09-20
updated: 2026-09-21
lang: "en"
tags:
  - "contributing"
  - "governance"
  - "workflow"
  - "git"
---

# Contributing to {PROJECT_NAME}

Thank you for your interest in contributing to **{PROJECT_NAME}**!  
We adhere to strict engineering standards, transparent architectural decision-making, and robust quality gates to ensure production stability.

---

## 🧭 Code of Conduct

All contributors and participants are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 🛠️ Development Workflow

We follow a feature branch workflow paired with **Conventional Commits**:

1. **Fork & Branch**:
   - Fork `{REPOSITORY_URL}` and create a dedicated branch:
     ```bash
     git checkout -b feature/my-enhancement
     ```
2. **Setup Environment & Hooks**:
   - Install local Git hooks to ensure secret leaks and formatting issues are caught before committing:
     ```bash
     python scripts/install-hooks.py
     ```
3. **Develop with Test-Driven Development (TDD)**:
   - Write tests that capture expected behavior before or alongside implementation.
   - Adhere to the general coding principles in `.agents/rules/coding-rules-general.md` and specific language rules in `.agents/rules/languages/`.
4. **Run Pre-Commit Verification**:
   - Ensure zero unresolved placeholders, strict adherence to file naming rules, and pass all linter checks:
     ```bash
     make check
     # Or run individually:
     python scripts/apply-template.py --check
     python scripts/validate-filenames.py
     ```
5. **Commit Message Conventions**:
   - Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
     - `feat: add new telemetry provider`
     - `fix: resolve race condition in cache eviction`
     - `docs: update getting started guide`
     - `refactor: streamline error handling logic`
     - `test: add unit coverage for authentication handler`

---

## 🤖 AI Coding & Assistant Guidelines

When developing with AI assistants (Google Antigravity, Claude Code, GitHub Copilot, Gemini CLI, Cursor):
- **Never bypass review**: AI-generated code must be reviewed and tested by a human before opening a PR.
- **Context Hierarchy**: Always respect enterprise governance and repository rules (`.agents/rules/`) over prompt suggestions.
- **Zero Secrets**: Do not allow AI tools to generate hardcoded mock keys, internal URLs, or real tokens.

---

## 📬 Submitting a Pull Request

1. Push your branch to your fork.
2. Open a Pull Request against the `main` branch of `{REPOSITORY_URL}`.
3. Fill out all sections of the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).
4. Verify that all automated GitHub Actions checks (CI, Gitleaks, Hygiene) pass.

---
title: Universal Naming Rules
description: Standardized naming conventions across kebab-case filenames, snake_case
  variables, and PascalCase types.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- naming-conventions
- standards
alwaysApply: true
globs:
- '**/*'
---
# General File & Directory Naming Rules (`naming-rules-general`)

All files and directories in this repository must strictly adhere to the following naming conventions to ensure consistency, prevent cross-platform file path issues, and facilitate automated AI agent workflows.

---

## 1. Agent Definitions (`.agents/agents/`)

- **Naming Pattern**: `<name>.agent.md`
- **Suffix Requirement**: Must end with `.agent.md`.
- **Forbidden Prefix**: **NEVER** use the `agent-` prefix (e.g. `agent-code-review.md` is strictly forbidden).
- **Casing**: Lowercase kebab-case for the name segment.
- **Examples**:
  - ✅ `code-review.agent.md`
  - ✅ `coding.agent.md`
  - ✅ `system-architect.agent.md`
  - ❌ `agent-code-review.md` (forbidden `agent-` prefix)
  - ❌ `CodeReview.agent.md` (uppercase letters)
  - ❌ `code_review.agent.md` (snake_case)

### Agent Language Profiles (`.agents/agents/languages/`)
- **Naming Pattern**: `coding-profile-<lang>.md` or `code-review-profile-<lang>.md`
- **Examples**: `coding-profile-python.md`, `code-review-profile-typescript.md`

---

## 2. Rules & Governance (`.agents/rules/`)

- **Naming Pattern**: `<category>-rules-<scope>.md`
- **Casing**: Lowercase kebab-case.
- **Examples**:
  - `coding-rules-general.md`
  - `naming-rules-general.md`
  - `security-rules-general.md`
  - `git-rules-commit.md`
  - `languages/coding-rules-python.md`

---

## 3. Workflows & Standard Operating Procedures (`.agents/workflows/`)

- **Naming Pattern**: `workflow-<name>.md`
- **Casing**: Lowercase kebab-case.
- **Examples**:
  - `workflow-spec-to-code.md`
  - `workflow-incident-response.md`

---

## 4. Skills Packages (`.agents/skills/`)

- **Directory Naming**: Lowercase kebab-case (`<category>-<name>` or `toolchain-<lang>`).
- **Entrypoint**: Every skill package must include a `SKILL.md` entrypoint.
- **Examples**:
  - `.agents/skills/git-workflow/SKILL.md`
  - `.agents/skills/code-review-gatekeeper/SKILL.md`
  - `.agents/skills/toolchain-python/SKILL.md`

---

## 5. Architectural Decision Records (`docs/adr/`)

- **Naming Pattern**: `NNNN-<slug>.md`
- **Numbering**: 4-digit sequential zero-padded number starting from `0000`.
- **Slug**: Lowercase kebab-case.
- **Examples**:
  - `docs/adr/0000-use-markdown-architectural-decision-records.md`
  - `docs/adr/0001-record-architecture-decisions.md`

---

## 6. General Files & Directories

- **Character Set**: Use only ASCII lowercase letters (`a-z`), numbers (`0-9`), hyphens (`-`), and dots (`.`).
- **No Whitespace**: Never include spaces or tab characters in file or folder names.
- **Root Exceptions**: Standard root-level Markdown files use uppercase (`README.md`, `README.ja.md`, `CLAUDE.md`, `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`).

---

## 7. Automated Verification & Enforcement

All commits and pull requests are automatically validated against these conventions:
- **Local Validation**: Run `python scripts/validate-filenames.py` (or `make check-names`).
- **Pre-commit Hook**: Installed via `python scripts/install-hooks.py` or `.pre-commit-config.yaml`.
- **CI Enforcement**: Enforced on every PR via GitHub Actions (`ci.yml`).

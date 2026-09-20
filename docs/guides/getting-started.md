---
title: "Getting Started with {PROJECT_NAME}"
description: "Step-by-step setup guide for local environment initialization, repository customization, and verification workflows."
category: "guide"
type: "tutorial"
status: "active"
date: 2026-09-20
updated: 2026-09-21
lang: "en"
tags:
  - "guide"
  - "getting-started"
  - "setup"
  - "tutorial"
---

# Getting Started with {PROJECT_NAME}

Welcome to **{PROJECT_NAME}**! This guide walks you through setting up your local environment and understanding repository standards.

---

## Prerequisites

- **Git** (version 2.30+)
- **Python 3.8+** (for template engine and automation scripts)
- Target language toolchain (e.g. Python, Node.js, Go, Rust, .NET, Dart, C/C++) depending on `{PRIMARY_LANGUAGE}`.

---

## 1. Local Initialization

If you just generated this repository from the template:

```bash
# 1. Inspect parameters in template.config.yaml
# Edit PROJECT_NAME, REPOSITORY_NAME, AUTHOR_NAME, etc.

# 2. Run dry-run to preview substitutions
python scripts/apply-template.py --dry-run

# 3. Apply substitutions across all files
python scripts/apply-template.py

# 4. Install Git Hooks to protect against secret leakage
python scripts/install-hooks.py
```

---

## 2. Directory Structure Conventions

- `src/` or package folder: Core source code.
- `tests/`: Automated unit, integration, and property-based test suites.
- `docs/`: Design documentation and Architectural Decision Records (`docs/adr/`).
- `.agents/`: AI agents, skill packages (`SKILL.md`), behavioral rules, and standard operating procedures.
- `scripts/`: Deterministic developer automation scripts.

---

## 3. Daily Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feat/user-authentication
   ```
2. Develop using Test-Driven Development (TDD).
3. Validate changes before committing:
   ```bash
   python scripts/apply-template.py --check
   ```
4. Commit following Conventional Commits (`feat:`, `fix:`, etc.).
5. Push branch and open a Pull Request.

---
title: "Gemini CLI & Antigravity Directives"
description: "Operational instructions, governance hierarchy, and rules integration for Gemini CLI and Google Antigravity agents."
category: "meta"
type: "configuration"
status: "active"
date: 2026-09-20
updated: 2026-10-03
lang: "en"
tags:
  - "gemini"
  - "antigravity"
  - "ai"
  - "configuration"
---

# Gemini CLI & Google Antigravity Instructions for {PROJECT_NAME}

- **Governance Model**: Two-Phase Governance (Plan & Review before Code Mutation).
- **Rules Reference**: Strictly adhere to `.agents/rules/coding-rules-general.md`, `.agents/rules/naming-rules-general.md`, and `.agents/rules/security-rules-general.md`.
- **Permission Tiers**: Follow `.agents/rules/permission-rules-general.md` (A: always allow, C: conditional, N: never). Install `.gemini/policies/permission-policy.toml` in `~/.gemini/policies/` to enforce it (see `docs/guides/ai-permission-guide.md`).
- **Naming Conventions**: Agent definitions MUST use `*.agent.md` suffix and MUST NOT prefix with `agent-`. Strictly follow `.agents/rules/naming-rules-general.md`.
- **Language Profile**: Load `.agents/agents/languages/coding-profile-{PRIMARY_LANGUAGE}.md` when operating on project code.
- **Skills Loading**: Leverage modular `SKILL.md` packages located in `.agents/skills/`.
- **Output Language**: Reply to the user and write PR titles/descriptions in Japanese; commit messages, code, identifiers, and comments stay in English. Details: `.agents/rules/git-rules-commit.md`.

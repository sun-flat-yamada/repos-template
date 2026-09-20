---
title: "Gemini CLI & Antigravity Directives"
description: "Operational instructions, governance hierarchy, and rules integration for Gemini CLI and Google Antigravity agents."
category: "meta"
type: "configuration"
status: "active"
date: 2026-09-20
updated: 2026-09-21
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
- **Naming Conventions**: Agent definitions MUST use `*.agent.md` suffix and MUST NOT prefix with `agent-`. Strictly follow `.agents/rules/naming-rules-general.md`.
- **Language Profile**: Load `.agents/agents/languages/coding-profile-{PRIMARY_LANGUAGE}.md` when operating on project code.
- **Skills Loading**: Leverage modular `SKILL.md` packages located in `.agents/skills/`.

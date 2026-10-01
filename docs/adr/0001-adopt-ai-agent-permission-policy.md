---
title: "ADR-0001: Adopt a Three-Tier AI Agent Permission Policy"
description: "Decision to classify every AI agent action as always allowed, conditionally allowed by a named condition, or never allowed, and to enforce the tiers through tool configuration, OS sandboxing, a PreToolUse guard hook, and server-side GitHub controls."
category: "adr"
type: "decision-record"
status: "proposed"
date: 2026-10-01
updated: 2026-10-01
lang: "en"
tags:
  - "adr"
  - "security"
  - "permissions"
  - "ai-agents"
---

# 1. Adopt a Three-Tier AI Agent Permission Policy

Date: 2026-10-01

## Status

Proposed

## Context

This template is used with several AI coding agents (Claude Code, Codex CLI, Gemini CLI / Antigravity, GitHub Copilot, Cursor). The existing rules in `.agents/rules/` describe intent in prose, but prose instructions do not restrict what an agent can execute. Public incidents in 2025–2026 show the failure modes: agents deleting production databases and home directories, prompt injection rewriting the agent's own settings to auto-approve everything (CVE-2025-53773), allowlisted commands chained with exfiltration (Gemini CLI, CVE-2025-55284), malicious packages launching agent CLIs with permission-bypass flags (Nx s1ngularity), and repository configuration executing code before the trust prompt (CVE-2025-59536, CVE-2026-21852).

Industry guidance converges on least agency (OWASP LLM06:2025, OWASP Agentic Top 10 2026), breaking the "lethal trifecta" of private data, untrusted input, and external communication (Agents Rule of Two), and explicit human approval gates for high-impact actions (CISA et al., *Careful Adoption of Agentic AI Services*, 2026). Each tool exposes a different permission format with different expressive power.

## Decision

1. Define one canonical policy, `.agents/rules/permission-rules-general.md`, with stable rule IDs in three tiers: **A** (always allow), **C** (conditionally allow, grouped by condition: C-SBX sandbox, C-NET allowlisted destination, C-SCOPE limited scope, C-HITL per-action human approval), and **N** (never allow).
2. Evaluate deny first; anything that matches no rule defaults to C-HITL, never to A.
3. Enforce the tiers in each tool's native format: `.claude/settings.json`, `.codex/config.toml` and `.codex/rules/permission-policy.rules`, `.gemini/settings.json` and `.gemini/policies/permission-policy.toml`, `.cursor/cli.json` and `.cursor/permissions.json`, and `.vscode/settings.json`. Where a tool cannot express a condition, choose the stricter tier.
4. Add `.claude/hooks/permission-guard.py`, a dependency-free PreToolUse hook with unit tests, to normalize command variants that pattern rules miss and to block writes that disable approvals. VS Code reuses it through `chat.useClaudeHooks`.
5. Require OS-level sandboxing for running project code (C-SBX) and pair local configuration with server-side controls: branch protection, CODEOWNERS review of agent and CI configuration, secret scanning, and CI-only publishing.

## Consequences

### Positive
- One reviewed source of truth with traceable rule IDs across all supported tools.
- High-impact actions (secrets, publishing, force push, production changes, guardrail bypass) are blocked in every mode, including auto-approve modes.
- Routine read-only work and sandboxed builds and tests run without prompt fatigue.

### Negative & Trade-offs
- More approval prompts for pushes, dependency changes, and network commands, especially where no sandbox is available (native Windows).
- Tool limitations force stricter-than-policy behavior in places (Cursor CLI has no ask list; Codex network access is all-or-nothing; Gemini CLI ignores workspace policies, so its policy must be copied to the user tier).
- Pattern rules and the guard hook are heuristics, not a security boundary; they must be maintained as tools evolve, and false positives (for example, commands that mention `.env`) are resolved in favor of denial.

---
title: "Architecture Overview - {PROJECT_NAME}"
description: "Architectural philosophy, layered model, and multi-agent AI ecosystem design for {PROJECT_NAME}."
category: "architecture"
type: "overview"
status: "active"
date: 2026-09-20
updated: 2026-09-21
lang: "en"
tags:
  - "architecture"
  - "clean-architecture"
  - "layered-model"
  - "ai-agents"
---

# Architecture Overview - {PROJECT_NAME}

## 1. Architectural Philosophy

`{PROJECT_NAME}` is designed around four foundational tenets:

1. **Isolation & Loose Coupling**: Clean boundaries between business domain logic, application interfaces, and infrastructure/transport adapters.
2. **Deterministic Quality Gates**: Continuous automated checks over subjective opinions. Every change must be validated through automated tests and strict linter rules.
3. **Multi-Agent AI Symbiosis**: Clear contracts and rules (`.agents/`) enabling human engineers and autonomous AI agents to collaborate seamlessly without architectural erosion.
4. **Defense-in-Depth**: Multi-layered secret and injection defenses embedded into everyday developer workflows.

---

## 2. Layered Architecture Model

```text
+--------------------------------------------------------------+
|                     External Interfaces                      |
|           (CLI, REST/GraphQL API, UI, Webhooks)             |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
|                  Application & Use Cases                     |
|           (Orchestration, Workflows, Commands)               |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
|                    Domain Core Logic                         |
|         (Entities, Pure Business Rules, Invariants)          |
+--------------------------------------------------------------+
                               ^
                               |
+--------------------------------------------------------------+
|                  Infrastructure & Adapters                   |
|        (Databases, Cloud Storage, External Clients)          |
+--------------------------------------------------------------+
```

- **Domain Core**: Zero external runtime dependencies. Business invariants are strictly protected here.
- **Application**: Coordinates domain entities and handles use-case execution.
- **Infrastructure**: Implements interfaces required by the domain/application layers (e.g. database repositories, cloud integrations).

---

## 3. Multi-Layer AI Ecosystem Design

Our `.agents/` hierarchy organizes AI guidance into clear levels:

1. **Constitutional Layer (`.agents/rules/coding-rules-general.md`)**:
   - Universal engineering standards (KISS, YAGNI, DRY, security guardrails).
2. **Language-Specific Layer (`.agents/rules/languages/`)**:
   - Deep idioms, memory safety guidelines, and performance considerations for C, C++, C#, TS, JS, Dart, Go, Rust, and Python.
3. **Execution Skills (`.agents/skills/`)**:
   - Portable, modular `SKILL.md` packages executing deterministic tasks (TDD cycles, Git operations, ADR scaffolding).

---
title: "Security Policy for {PROJECT_NAME}"
description: "Vulnerability reporting protocols, coordinated disclosure policies, and supported release versions for {PROJECT_NAME}."
category: "governance"
type: "policy"
status: "active"
date: 2026-09-20
updated: 2026-09-21
lang: "en"
tags:
  - "security"
  - "vulnerability"
  - "disclosure"
  - "policy"
---

# Security Policy for {PROJECT_NAME}

## Supported Versions

We provide security patches and dependency updates for the following versions:

| Version | Supported          | Security Fixes |
| :---    | :---               | :---           |
| 1.0.x   | :white_check_mark: | Active         |
| < 1.0.0 | :x:                | End of Life    |

---

## Reporting a Vulnerability

We take the security, integrity, and privacy of **{PROJECT_NAME}** seriously.

If you discover a security vulnerability, credential exposure, or prompt injection threat (e.g. indirect prompt injection / "Clinejection" vectors):

1. **DO NOT** create a public GitHub Issue.
2. Please report the concern via **GitHub Private Vulnerability Reporting** by navigating to the **Security** tab of this repository and selecting **Report a vulnerability**.
3. Alternatively, report confidentially to the maintainer via email: `{AUTHOR_EMAIL}`.

### Vulnerability Report Checklist
Please include:
- A clear description of the vulnerability and its potential impact.
- Step-by-step reproduction instructions or a minimal proof of concept (PoC).
- Affected components, configurations, or external dependencies.
- Any proposed remediations or mitigation workarounds.

We will acknowledge receipt within 48 hours and work with you on a responsible disclosure timeline.

---

## Multi-Layered Defense-in-Depth Architecture

This repository adopts a 4-layer defense-in-depth model aligned with OWASP Top 10, Gitleaks, and modern AI engineering standards:

### Layer 1: AI Agent Guardrails & Behavioral Rules (`.agents/rules/`)
- AI coding assistants are bound by mandatory directives prohibiting hardcoded secrets, plain API tokens, mock cryptographic keys, and PII leakage.
- Security-sentinel reviews inspect every proposal for indirect prompt injection vectors before merging.

### Layer 2: Local & Git Exclusion Hygiene (`.gitignore`)
- Strict exclusion patterns cover private keys (`*.pem`, `id_rsa`), certificates (`*.crt`), cloud provider credentials (`.aws/`, `.gcp/`, `service_account*.json`), `.env*`, and local development dumps.

### Layer 3: Pre-Commit & Local Verification (`.githooks/`)
- Pre-commit hooks run secret pattern scanning and placeholder validation before commits can be finalized locally.

### Layer 4: Automated CI/CD Enforcement (`.github/workflows/secret-scan.yml`)
- Automated Gitleaks scanning runs on every push and pull request to prevent accidental leakage into the repository history.

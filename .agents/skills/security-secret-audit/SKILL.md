---
name: "security-secret-audit"
description: "Audits repository files, diffs, and configuration for hardcoded secrets, private keys, API credentials, and indirect prompt injection vulnerabilities."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*"
tags:
  - "skill"
  - "security"
  - "secret-audit"
  - "compliance"
  - "vulnerability"
---
# Skill: Security & Secret Audit (`security-secret-audit`)

## Instructions
1. **File Type Screening**:
   - Verify that no private keys (`.pem`, `.key`, `id_rsa`), certificates (`.crt`), or environment files (`.env`) are being tracked in git index.
2. **Entropy & Pattern Matching**:
   - Search staged and modified content for high-entropy strings and common token regexes:
     - GitHub Tokens: `ghp_[A-Za-z0-9_]{36}`
     - AWS Keys: `AKIA[0-9A-Z]{16}`
     - Generic API Keys: `(?i)(api[_-]?key|secret|password|bearer)[ \t]*[=:][ \t]*['\"][A-Za-z0-9_\-\.]{16,}['\"]`
3. **Indirect Prompt Injection Check**:
   - Inspect issue templates and external prompt inputs to ensure proper boundary tags (`<untrusted_content>`) are utilized.
4. **Remediation**:
   - Immediately unstage any detected secret file (`git rm --cached <file>`).
   - If a secret was committed to history, guide maintainers on using `git filter-repo` and revoking the compromised credential immediately.

## Best Practices
- Never output real discovered secret values in log messages; mask them (e.g. `ghp_****`).
- Local git hooks (`.githooks/pre-commit`) must always be kept active.

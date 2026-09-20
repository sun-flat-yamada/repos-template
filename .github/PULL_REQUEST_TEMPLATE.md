---
title: "Pull Request Template"
description: "Standard pull request template outlining change categories, test verification checklists, and security sign-offs."
category: "meta"
type: "template"
status: "active"
date: 2026-09-20
updated: 2026-09-21
lang: "en"
tags:
  - "github"
  - "pull-request"
  - "template"
  - "verification"
---

## 📝 Description
<!-- A clear and concise description of what this PR does and why it is needed. -->

Fixes #(issue)

---

## 🔍 Type of Change
- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] ✨ New feature (non-breaking change adding functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] ♻️ Refactoring (no functional changes, code cleanup)
- [ ] 📚 Documentation update
- [ ] 🧪 Tests (adding missing tests or fixing existing tests)
- [ ] ⚙️ CI/CD / Infrastructure update

---

## 🧪 Verification & Testing
<!-- Describe the tests you ran to verify your changes. Include steps so others can reproduce. -->

- [ ] Automated unit/integration tests pass locally
- [ ] Linter/formatter checks pass (`make check` or equivalent)
- [ ] Zero secret leaks or unintended tokens in code or commit history
- [ ] Manual testing performed:
  <!-- Describe manual test results -->

---

## 🔒 Security & Governance Checklist
- [ ] No hardcoded credentials, API keys, or private tokens committed.
- [ ] Inputs are sanitized and indirect prompt injection vectors mitigated.
- [ ] Architecture aligns with ADRs in `docs/adr/` (if architectural changes are introduced).
- [ ] Conventional Commit format used for all commits (`feat:`, `fix:`, etc.).

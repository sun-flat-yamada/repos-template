---
title: "Workflow: Incident Response & Defect Triage"
description: "Standard operating procedure for defect triage, vulnerability containment, credential revocation, and post-mortems."
category: "workflow"
type: "sop"
status: "active"
date: 2026-09-20
updated: 2026-09-21
lang: "en"
tags:
  - "workflow"
  - "incident-response"
  - "security"
  - "sop"
---

# Standard Operating Procedure: Incident Response & Defect Triage (`workflow-incident-response`)

This SOP guides maintainers and security sentinels when responding to defects, security alerts, or indirect prompt injection threats.

---

## 1. Triage & Classification
1. **Severity Assessment**:
   - **P0 (Critical)**: Active credential leak, remote code execution vulnerability, system outage.
   - **P1 (High)**: Broken core feature, data corruption, severe performance regression.
   - **P2 (Medium)**: Non-critical edge case defect, cosmetic flaw with workaround.
   - **P3 (Low)**: Minor documentation typo, minor code style issue.
2. **Confidentiality Check**:
   - If the report involves a security vulnerability or leaked secret, move immediately to private advisory channels (see `SECURITY.md`). Do not comment publicly.

---

## 2. Containment & Remediation
1. **Credential Invalidation**:
   - If a token or key was exposed, immediately revoke and rotate the credential in the relevant cloud provider or third-party service.
2. **History Rewriting (if required)**:
   - Use `git filter-repo` to scrub sensitive data from git history if pushed upstream.
3. **Reproduction Test**:
   - Author a test case reproducing the reported vulnerability or bug before attempting a fix.

---

## 3. Patching & Post-Mortem
1. Implement the minimal fix.
2. Verify all test suites pass.
3. If an architectural weakness allowed the flaw, record an ADR in `docs/adr/` with preventive mitigations.

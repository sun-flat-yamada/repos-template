---
title: Documentation Rules
description: Mandatory documentation standards, synchronization requirements, markdown
  formatting, and YAML front-matter rules.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- documentation
- front-matter
- standards
alwaysApply: false
globs:
- '**/*.md'
- docs/**/*
---
# Documentation Rules (`doc-rules-general`)

Documentation is a first-class citizen of this repository.

## 1. Synchronization with Code
- Code changes that alter public APIs, configuration keys, or CLI parameters must include corresponding updates to `README.md`, `README.ja.md`, and relevant files in `docs/`.
- Never submit a pull request where implementation and documentation disagree.

## 2. Architectural Decision Records (ADRs)
- Significant decisions regarding architecture, language versions, major libraries, or data persistence patterns must be documented in `docs/adr/`.
- Use the format defined in `docs/adr/template.md`.

## 3. Markdown Formatting Standards
- Use standard GitHub Flavored Markdown (GFM).
- Fenced code blocks must always declare their language (e.g. ```python, ```bash, ```mermaid).
- Relative links within the repository must use forward slashes (`/`) and point to valid, existing paths.

## 4. File & Directory Naming Standards
- All new files and directories must strictly comply with `.agents/rules/naming-rules-general.md`.
- Agent definition files MUST use the `*.agent.md` suffix and MUST NOT prefix with `agent-`.
- Avoid spaces and non-standard characters across all filenames.

## 5. Front-Matter Metadata Standards
- All markdown documentation (`*.md`) across root and `docs/` must include a valid YAML front-matter block.
- Front-matter must strictly adhere to the guidelines specified in `docs/guides/front-matter-standards.md`.
- Required fields include `title` and a high-density, informative `description` for human clarity and AI/RAG indexing.
- Ensure all dates use ISO 8601 (`YYYY-MM-DD`) and strings with colons are enclosed in double quotes.


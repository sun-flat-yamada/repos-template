---
title: 'Code Review Profile: Python'
description: Auditing standards, idiomatic patterns, memory safety, and common anti-patterns
  for Python codebases.
category: agent-profile
type: review-profile
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- agent
- profile
- code-review
- python
alwaysApply: false
globs:
- '**/*.py'
- '**/pyproject.toml'
- '**/requirements*.txt'
- '**/setup.py'
---
# Code Review Profile: Python (`code-review-profile-python`)

Focus on high-impact defects and production stability. Disregard mechanical formatting (entrusted to Ruff).

---

## 🔍 High-Signal Review Checklist

### 1. Concurrency & Async Pitfalls
- [ ] **[P0-BLOCKER] Cancellation Leak**: Are all async network sessions, database connections, and locks wrapped in `async with` or `try...finally`?
- [ ] **[P0-BLOCKER] Blocking Call in Event Loop**: Is synchronous I/O (e.g. `time.sleep()`, standard `open()`, synchronous `requests.get()`) executed inside an `async def` without `asyncio.to_thread()`?
- [ ] **[P1-DEFECT] Fire-and-Forget Task Leak**: Are background tasks created with `asyncio.create_task()` stored in a strong reference set, or do they risk garbage collection mid-execution?

### 2. Error Handling & Traceability
- [ ] **[P1-DEFECT] Swallowed Exception / Missing Chain**: Does an `except` block raise a new exception without `from err`? Does an `except Exception:` block lack logging of the original traceback?
- [ ] **[P1-DEFECT] Bare `except:`**: Flag any untyped `except:` immediately; it catches `KeyboardInterrupt` and `SystemExit`.

### 3. Data Integrity & Types
- [ ] **[P0-BLOCKER] Naive Datetime**: Is `datetime.now()` used without UTC timezone? Will it cause comparison crashes or database timezone distortion?
- [ ] **[P1-DEFECT] Mutable Default Parameter**: Does any function define default arguments with `[]`, `{}`, or instance objects?
- [ ] **[P2-MAINTENANCE] Untyped Public Boundary**: Does any exported function omit argument or return type annotations, or rely on `Any`?

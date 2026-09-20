---
title: 'Code Review Profile: Dart'
description: Auditing standards, idiomatic patterns, memory safety, and common anti-patterns
  for Dart codebases.
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
- dart
alwaysApply: false
globs:
- '**/*.dart'
- '**/pubspec.yaml'
- '**/analysis_options.yaml'
---
# Code Review Profile: Dart (`code-review-profile-dart`)

Focus on async gap safety, stream leaks, and sound null safety.

---

## 🔍 High-Signal Review Checklist

### 1. Async & Context Safety
- [ ] **[P0-BLOCKER] Async Gap Context Use**: Is `BuildContext` referenced after an `await` statement without an `if (!context.mounted) return;` check?
- [ ] **[P0-BLOCKER] StreamSubscription Leak**: Does any class subscribing to a `Stream` fail to cancel the subscription on teardown/dispose?
- [ ] **[P1-DEFECT] Unawaited Background Future**: Are background asynchronous operations invoked without `unawaited()` and error catching?

### 2. Error Handling & Null Safety
- [ ] **[P1-DEFECT] Swallowed Exception**: Does an empty `catch (e) {}` exist in the codebase?
- [ ] **[P1-DEFECT] Fragile Null Assertion**: Is the `!` operator used on nullable variables where a graceful default (`??`) or guard check should be used?

### 3. Idiomatic Style
- [ ] **[P2-MAINTENANCE] Non-Standard Documentation**: Are doc comments written with `//` or `/* */` instead of Effective Dart `///`?

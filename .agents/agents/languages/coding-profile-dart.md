---
title: 'Coding Profile: Dart'
description: Production implementation standards, architectural idioms, dependency
  hygiene, and testing guidelines for Dart.
category: agent-profile
type: coding-profile
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- agent
- profile
- coding
- dart
alwaysApply: false
globs:
- '**/*.dart'
- '**/pubspec.yaml'
- '**/analysis_options.yaml'
---
# Coding Profile: Dart (`coding-profile-dart`)

## Target Standards
- **Standard Version**: Dart 3.x+ (Sound Null Safety)
- **Primary Toolchain**: `dart analyze --fatal-infos`, `dart test`, `dart format`

---

## 🎯 Critical Engineering Safeguards (High-Impact Idioms)

### 1. Async Gap & Context Mounting
- **Rule**: In Flutter / client applications, NEVER access `BuildContext` across an `await` boundary without first checking `if (!context.mounted) return;`.
- **Anti-Pattern (Crash on Navigation)**:
  ```dart
  // BAD: If user navigated away during fetch, context is unmounted -> Crash
  await fetchData();
  Navigator.of(context).pop(); 
  ```
- **Resilient Idiom**:
  ```dart
  // GOOD: Guard against unmounted context
  await fetchData();
  if (!context.mounted) return;
  Navigator.of(context).pop();
  ```

### 2. StreamSubscription & Resource Cancellation
- **Rule**: Every `StreamSubscription` must be explicitly cancelled in `dispose()` or cleanup routines to prevent memory and callback leaks.

### 3. Floating Future Handling
- **Rule**: If a `Future` is intentionally executed in the background, use `unawaited(future)` from `dart:async` and attach an `.onError` or `catchError` handler.

### 4. Banned Antipatterns
- Empty `catch` blocks (`catch (e) {}`). Always log or handle.
- Indiscriminate use of `!` (null assertion) without preceding verification.

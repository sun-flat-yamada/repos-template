---
title: 'Language Coding Rules: Dart'
description: Language-specific style guidelines, static analysis requirements, and
  best practices for Dart.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- language-rules
- dart
alwaysApply: false
globs:
- '**/*.dart'
- '**/pubspec.yaml'
- '**/analysis_options.yaml'
---
# Language Coding Rules: Dart (`coding-rules-dart`)

## 1. Sound Null Safety & Modern Features
- Write with Sound Null Safety. Avoid `!` (null assertion) unless preceded by an explicit null check.
- Use Dart 3 switch expressions and pattern matching for algebraic data type destructuring.
- Prefer concise primary constructor syntax (`class Point(this.x, this.y);` or `const Point({required this.x, required this.y});`).
- Make data structures immutable by default (`final` fields, `const` constructors).

## 2. Effective Dart Guidelines
- Follow official [Effective Dart](https://dart.dev/effective-dart) style and documentation guidelines (`///` for documentation comments).
- Specify explicit types on public API boundaries; use `var` or `final` for local variable inference.
- Avoid unhandled asynchronous errors: always await `Future` or register error callbacks.

## 3. Tooling & Enforcement
- Run `dart analyze --fatal-infos` in CI.
- Enforce formatting with `dart format --output=none --set-exit-if-changed .`.

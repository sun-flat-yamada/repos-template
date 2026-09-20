---
title: 'Language Coding Rules: C++'
description: Language-specific style guidelines, static analysis requirements, and
  best practices for C++.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- language-rules
- cpp
alwaysApply: false
globs:
- '**/*.cpp'
- '**/*.hpp'
- '**/*.cc'
- '**/*.cxx'
- '**/*.h'
- '**/CMakeLists.txt'
---
# Language Coding Rules: C++ (`coding-rules-cpp`)

## 1. Resource Management & Modern C++
- **Zero Raw Pointers for Ownership**: Use `std::unique_ptr` for exclusive ownership, `std::shared_ptr` for shared ownership, and `std::weak_ptr` to break cyclic references.
- **Rule of Zero / Five**:
  - Prefer the Rule of Zero: let standard library containers handle cleanup.
  - If custom resource handling is needed, explicitly declare or delete all five special member functions (destructor, copy constructor, copy assignment, move constructor, move assignment).
- **No `NULL` or `0`**: Use `nullptr` exclusively.

## 2. Type Safety & API Design
- Const correctness: Member functions that do not mutate state must be marked `const`.
- Mark single-argument constructors as `explicit` to prevent unintended implicit conversions.
- Pass complex objects by `const &` (or by value when transferring ownership with `std::move`).
- Use `std::string_view` for read-only string parameters where null-termination is not required.

## 3. Tooling & Enforcement
- Enforce formatting using `.clang-format`.
- Run Clang-Tidy checks in CI and test builds with AddressSanitizer and UndefinedBehaviorSanitizer.

---
title: 'Coding Profile: C++'
description: Production implementation standards, architectural idioms, dependency
  hygiene, and testing guidelines for C++.
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
# Coding Profile: C++ (`coding-profile-cpp`)

## Target Standards
- **Standard Version**: Modern C++ (C++20 / C++23)
- **Primary Toolchain**: CMake, Clang-Tidy, Clang-Format, Sanitizers (`-fsanitize=address,undefined`)

---

## 🎯 Critical Engineering Safeguards (High-Impact Idioms)

### 1. Dangling References with `std::string_view` & Ranges
- **Rule**: NEVER bind `std::string_view` or C++20 range views to temporary objects returned by value.
- **Anti-Pattern (Silent Memory Corruption)**:
  ```cpp
  // BAD: get_temporary_string() is destroyed at semicolon; sv becomes dangling!
  std::string_view sv = get_temporary_string();
  process(sv); // Undefined Behavior / Crash in production
  ```
- **Resilient Idiom**:
  ```cpp
  // GOOD: Extend lifetime by binding to a local std::string first
  std::string s = get_temporary_string();
  std::string_view sv = s;
  process(sv);
  ```

### 2. Strict RAII & No Raw Pointer Ownership
- **Rule**: Dynamic memory MUST be managed exclusively via `std::unique_ptr` or `std::shared_ptr`. Zero raw `new` / `delete`.
- **Idiom**: Always use `std::make_unique<T>()` and `std::make_shared<T>()`.

### 3. Use-After-Move Defense
- **Rule**: Once an object is moved via `std::move(obj)`, treat it as moved-from and do not inspect its state unless reinitialized.

### 4. Banned Antipatterns
- C-style casts (`(int)x`). Use `static_cast`, `reinterpret_cast`, or `std::bit_cast`.
- Raw C arrays (`int arr[10]`). Use `std::array<int, 10>` or `std::vector<int>`.
- Non-virtual destructors on polymorphic base classes.

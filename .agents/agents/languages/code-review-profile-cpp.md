---
title: 'Code Review Profile: C++'
description: Auditing standards, idiomatic patterns, memory safety, and common anti-patterns
  for C++ codebases.
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
# Code Review Profile: C++ (`code-review-profile-cpp`)

Focus on lifetime bugs, undefined behavior, and modern C++ correctness.

---

## 🔍 High-Signal Review Checklist

### 1. Lifetime & Memory Safety
- [ ] **[P0-BLOCKER] Dangling View / Reference**: Does any `std::string_view` or `std::span` point to a temporary rvalue?
- [ ] **[P0-BLOCKER] Raw Ownership**: Is `new` or `delete` used directly instead of `std::unique_ptr`?
- [ ] **[P0-BLOCKER] Non-Virtual Polymorphic Destructor**: Does a polymorphic base class declare a non-virtual destructor? (Causes incomplete destruction and leak).
- [ ] **[P1-DEFECT] Use-After-Move**: Is any variable accessed after being passed to `std::move()`?

### 2. Modern Concurrency & Exceptions
- [ ] **[P0-BLOCKER] Exception in Destructor**: Does any destructor throw or allow exceptions to escape without `noexcept`? (Triggers immediate `std::terminate`).
- [ ] **[P1-DEFECT] Unsynchronized Shared Access**: Are multi-threaded reads/writes to containers or primitives protected with `std::mutex` or `std::atomic`?

### 3. Idiomatic Modern Standards
- [ ] **[P2-MAINTENANCE] Missing `explicit`**: Are single-argument constructors missing the `explicit` specifier?
- [ ] **[P2-MAINTENANCE] C-Style Casts**: Are raw C casts `(Type)val` present instead of explicit C++ casts?

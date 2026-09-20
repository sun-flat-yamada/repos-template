---
title: 'Language Coding Rules: C'
description: Language-specific style guidelines, static analysis requirements, and
  best practices for C.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- language-rules
- c
alwaysApply: false
globs:
- '**/*.c'
- '**/*.h'
- '**/Makefile'
- '**/CMakeLists.txt'
---
# Language Coding Rules: C (`coding-rules-c`)

## 1. Safety & Memory Management
- **Explicit Pointer Verification**: Check all pointers for `NULL` before dereferencing.
- **Initialization**: Always initialize variables at declaration time (e.g. `int count = 0;`, `char *ptr = NULL;`).
- **Bounded Buffer Manipulation**:
  - Prohibit `strcpy`, `strcat`, `sprintf`, `vsprintf`, `gets`.
  - Use `strncpy`, `strncat`, `snprintf` ensuring the null-terminator is explicitly placed at `buf[size - 1] = '\0'`.
- **Resource Ownership**:
  - Every resource allocation function (`init_*`, `create_*`) must have an exact teardown counterpart (`free_*`, `destroy_*`).

## 2. Types & Standards
- Use fixed-width integer types from `<stdint.h>` (`int32_t`, `uint64_t`, `size_t`) instead of raw `long` or `unsigned int`.
- Use `bool` from `<stdbool.h>` rather than integer flags.
- Const correctness: Apply `const` to all read-only pointer parameters (`const char *src`).

## 3. Tooling & Enforcement
- Build with: `-Wall -Wextra -Wpedantic -Werror -Wconversion -Wshadow`.
- Run `clang-tidy` and AddressSanitizer (`-fsanitize=address`) during test execution.

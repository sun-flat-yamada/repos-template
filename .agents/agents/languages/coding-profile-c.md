---
title: 'Coding Profile: C'
description: Production implementation standards, architectural idioms, dependency
  hygiene, and testing guidelines for C.
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
- c
alwaysApply: false
globs:
- '**/*.c'
- '**/*.h'
- '**/Makefile'
- '**/CMakeLists.txt'
---
# Coding Profile: C (`coding-profile-c`)

## Target Standards
- **Standard Version**: C11 / C17 / C23
- **Primary Toolchain**: `gcc`/`clang` (`-Wall -Wextra -Wpedantic -Werror -fsanitize=address,undefined`)

---

## 🎯 Critical Engineering Safeguards (High-Impact Idioms)

### 1. Safe `realloc` Pattern
- **Rule**: NEVER assign `realloc` directly to the original pointer variable. If `realloc` fails, it returns `NULL` and the original memory block is permanently leaked!
- **Anti-Pattern (Silent Leak)**:
  ```c
  // BAD: If allocation fails, ptr becomes NULL and original block is leaked!
  ptr = realloc(ptr, new_size);
  ```
- **Resilient Idiom**:
  ```c
  // GOOD: Check temporary pointer first
  void *tmp = realloc(ptr, new_size);
  if (tmp == NULL) {
      // Handle allocation error; ptr remains intact and can be freed safely
      free(ptr);
      return -1;
  }
  ptr = tmp;
  ```

### 2. Integer Overflow Defense
- **Rule**: Never assume signed integer overflow wraps around (in C, signed overflow is Undefined Behavior and compilers will optimize away checks like `x + 1 > x`).
- **Idiom**: Check limits before performing arithmetic:
  ```c
  if (a > INT_MAX - b) {
      /* handle overflow */
  }
  ```

### 3. Proper `snprintf` Truncation Checking
- **Rule**: `snprintf` returns the number of characters that *would* have been written, NOT what was actually written.
- **Idiom**:
  ```c
  int n = snprintf(buf, sizeof(buf), "%s", src);
  if (n < 0 || (size_t)n >= sizeof(buf)) {
      /* String was truncated or error occurred */
  }
  ```

### 4. Banned Antipatterns
- Unbounded functions: `gets`, `strcpy`, `strcat`, `sprintf`.
- Calling non-reentrant / non-async-signal-safe functions (`printf`, `malloc`) inside signal handlers.

---
name: "toolchain-c"
description: "Executes C compiler toolchain operations including compilation (gcc/clang), static analysis (clang-tidy), and automated test runners (ctest/unity)."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.c"
  - "**/*.h"
  - "**/Makefile"
  - "**/CMakeLists.txt"
tags:
  - "skill"
  - "toolchain"
  - "c"
  - "build"
  - "test"
---
# Skill: C Toolchain (`toolchain-c`)

## Instructions
1. **Compilation**:
   ```bash
   # Strict compilation with sanitizers
   gcc -Wall -Wextra -Wpedantic -Werror -fsanitize=address,undefined -g src/*.c -o bin/app
   ```
2. **Static Analysis**:
   ```bash
   clang-tidy src/*.c -- -Iinclude
   ```
3. **Testing**:
   ```bash
   # Run CTest if using CMake
   ctest --output-on-failure
   ```

## Best Practices
- Always test under AddressSanitizer and UndefinedBehaviorSanitizer before committing.
- Ensure zero warnings emitted under `-Wall -Wextra -Wpedantic`.

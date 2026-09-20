---
name: "toolchain-cpp"
description: "Executes modern C++ build workflows using CMake, Clang-Format, Clang-Tidy, and Google Test / Catch2 test harnesses."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.cpp"
  - "**/*.hpp"
  - "**/*.cc"
  - "**/*.cxx"
  - "**/*.h"
  - "**/CMakeLists.txt"
tags:
  - "skill"
  - "toolchain"
  - "cpp"
  - "build"
  - "test"
---
# Skill: C++ Toolchain (`toolchain-cpp`)

## Instructions
1. **Configure & Build with CMake**:
   ```bash
   cmake -B build -S . -DCMAKE_BUILD_TYPE=Debug -DENABLE_SANITIZERS=ON
   cmake --build build -j
   ```
2. **Formatting & Linting**:
   ```bash
   clang-format -i src/**/*.cpp include/**/*.hpp
   clang-tidy -p build src/**/*.cpp
   ```
3. **Testing**:
   ```bash
   ctest --test-dir build --output-on-failure
   ```

## Best Practices
- Keep build configurations strictly out-of-source (`build/`).
- Enforce formatting using `.clang-format`.

---
name: "toolchain-dart"
description: "Executes Dart SDK operations including package resolution, static analysis (dart analyze), formatting (dart format), and automated testing (dart test)."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.dart"
  - "**/pubspec.yaml"
  - "**/analysis_options.yaml"
tags:
  - "skill"
  - "toolchain"
  - "dart"
  - "build"
  - "test"
---
# Skill: Dart Toolchain (`toolchain-dart`)

## Instructions
1. **Package Resolution**:
   ```bash
   dart pub get
   ```
2. **Static Analysis & Formatting**:
   ```bash
   dart analyze --fatal-infos
   dart format --output=none --set-exit-if-changed .
   ```
3. **Automated Testing**:
   ```bash
   dart test --coverage=coverage
   ```
4. **Mechanical Fixes**:
   ```bash
   dart fix --apply
   ```

## Best Practices
- Keep sound null safety verified at all times.
- Ensure all doc comments follow Effective Dart three-slash (`///`) convention.

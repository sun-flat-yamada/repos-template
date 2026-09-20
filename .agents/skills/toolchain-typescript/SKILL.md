---
name: "toolchain-typescript"
description: "Executes TypeScript toolchain tasks including typechecking with tsc, linting with ESLint/Biome, and unit testing via Vitest/Jest."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/tsconfig*.json"
  - "**/package.json"
tags:
  - "skill"
  - "toolchain"
  - "typescript"
  - "build"
  - "test"
---
# Skill: TypeScript Toolchain (`toolchain-typescript`)

## Instructions
1. **Typecheck**:
   ```bash
   npx tsc --noEmit
   ```
2. **Lint & Format**:
   ```bash
   # Using ESLint or Biome
   npx eslint . --max-warnings 0
   # or: npx @biomejs/biome check --write .
   ```
3. **Automated Testing**:
   ```bash
   npx vitest run --coverage
   ```

## Best Practices
- Never bypass type errors with `@ts-ignore` without explicit peer sign-off.
- Verify that `tsconfig.json` retains `"strict": true`.

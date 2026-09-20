---
name: "toolchain-javascript"
description: "Executes modern ECMAScript/JavaScript toolchain workflows including Node.js test runner, Biome formatting, and ESLint analysis."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.mjs"
  - "**/*.cjs"
  - "**/package.json"
tags:
  - "skill"
  - "toolchain"
  - "javascript"
  - "build"
  - "test"
---
# Skill: JavaScript Toolchain (`toolchain-javascript`)

## Instructions
1. **Linting & Formatting**:
   ```bash
   npx eslint .
   # or: npx prettier --check .
   ```
2. **Automated Testing**:
   ```bash
   # Using native Node.js test runner
   node --test tests/**/*.test.js
   # or with Vitest
   npx vitest run
   ```

## Best Practices
- Ensure package is configured as ESM (`"type": "module"` in `package.json`).
- Ensure all public APIs include valid JSDoc type annotations.

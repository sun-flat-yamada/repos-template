---
title: 'Coding Profile: TypeScript'
description: Production implementation standards, architectural idioms, dependency
  hygiene, and testing guidelines for TypeScript.
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
- typescript
alwaysApply: false
globs:
- '**/*.ts'
- '**/*.tsx'
- '**/tsconfig*.json'
- '**/package.json'
---
# Coding Profile: TypeScript (`coding-profile-typescript`)

## Target Standards
- **Standard Version**: TypeScript 5.5+ (ES2024 / Node 20+)
- **Primary Toolchain**: `tsc --noEmit`, `eslint` / `biome`, `vitest`

---

## 🎯 Critical Engineering Safeguards (High-Impact Idioms)

### 1. Banning Unsafe Type Assertions (`as SomeType`)
- **Rule**: Never use `as T` to silence the compiler. It provides zero runtime validation and leads to `TypeError: Cannot read properties of undefined` in production.
- **Anti-Pattern (False Security)**:
  ```typescript
  // BAD: Crashes at runtime if API shape changes or returns null
  const user = (await res.json()) as User;
  console.log(user.profile.name);
  ```
- **Resilient Idiom (Runtime Schema Validation)**:
  ```typescript
  // GOOD: Parse with Zod/ArkType. Fails fast with descriptive diagnostic if invalid
  import { z } from "zod";

  const UserSchema = z.object({
    id: z.string(),
    profile: z.object({ name: z.string() })
  });

  const raw = await res.json();
  const user = UserSchema.parse(raw); // user is strongly typed and runtime-verified
  ```

### 2. Floating Promise Prevention
- **Rule**: Every `Promise` must be awaited or explicitly attached to a `.catch()` handler. Unhandled floating promises lead to silent background failures.
- **Anti-Pattern**:
  ```typescript
  // BAD: If sendAnalytics fails, error is swallowed or triggers UnhandledPromiseRejection
  function handleClick() {
    sendAnalytics("click"); // Floating promise!
  }
  ```
- **Resilient Idiom**:
  ```typescript
  // GOOD: Await or void with explicit catch
  async function handleClick() {
    await sendAnalytics("click");
  }
  // OR if fire-and-forget is truly intended:
  void sendAnalytics("click").catch((err) => logger.error("Analytics failure", { err }));
  ```

### 3. Exhaustiveness Checking for Discriminated Unions
- **Rule**: In `switch` statements over domain union states, always enforce exhaustive matching using `assertNever(x: never)`.
  ```typescript
  function assertNever(x: never): never {
    throw new Error(`Unexpected object: ${JSON.stringify(x)}`);
  }
  ```

### 4. Banned Antipatterns
- Prohibit `any`; use `unknown` with type narrowing.
- Prohibit non-null assertion `!` unless immediately preceded by a checked condition.

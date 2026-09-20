---
title: 'Language Coding Rules: C#'
description: Language-specific style guidelines, static analysis requirements, and
  best practices for C#.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- language-rules
- csharp
alwaysApply: false
globs:
- '**/*.cs'
- '**/*.csproj'
- '**/*.sln'
---
# Language Coding Rules: C# (`coding-rules-csharp`)

## 1. Nullability & Type System
- Always enable `<Nullable>enable</Nullable>` in `.csproj`.
- Use the null-forgiving operator (`!`) only when static analysis cannot infer safety and document why.
- Prefer `record` and `record struct` for immutable value objects and DTOs.
- Use pattern matching (`switch` expressions, `is` expressions) for expressive conditional logic.

## 2. Async & Concurrency
- Append `Async` suffix to all asynchronous method names.
- Always accept a `CancellationToken cancellationToken = default` parameter in async methods that perform I/O.
- Configure awaits with `.ConfigureAwait(false)` in non-UI / library code.
- Implement `IAsyncDisposable` for asynchronous resource cleanup.

## 3. Tooling & Formatting
- Enforce formatting using `dotnet format --verify-no-changes` in CI.
- Treat compiler warnings as errors (`<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`).

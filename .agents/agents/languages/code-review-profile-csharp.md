---
title: 'Code Review Profile: C#'
description: Auditing standards, idiomatic patterns, memory safety, and common anti-patterns
  for C# codebases.
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
- csharp
alwaysApply: false
globs:
- '**/*.cs'
- '**/*.csproj'
- '**/*.sln'
---
# Code Review Profile: C# (`code-review-profile-csharp`)

Focus on async reliability, memory leaks, and .NET runtime performance.

---

## 🔍 High-Signal Review Checklist

### 1. Asynchronous Hygiene
- [ ] **[P0-BLOCKER] `async void` Detection**: Is `async void` used anywhere other than a top-level UI event handler?
- [ ] **[P0-BLOCKER] Sync-over-Async Deadlock**: Does any code call `.Result`, `.Wait()`, or `.GetAwaiter().GetResult()` on a `Task`?
- [ ] **[P1-DEFECT] Missing `CancellationToken`**: Do public asynchronous methods omit `CancellationToken ct = default` propagation?

### 2. Resource & Memory Discipline
- [ ] **[P0-BLOCKER] Unmanaged Resource Leak**: Are objects implementing `IDisposable` or `IAsyncDisposable` created without `using var` or `await using var`?
- [ ] **[P1-DEFECT] Multiple LINQ Enumeration**: Is an `IEnumerable<T>` evaluated multiple times without materialization (`.ToList()`)?
- [ ] **[P1-DEFECT] Primary Constructor Mutable State**: In a class using primary constructors, are parameters accidentally mutated across method calls?

### 3. Nullability & Types
- [ ] **[P1-DEFECT] Unsafe Null Suppression**: Is `!` used without a preceding null check or architectural proof?
- [ ] **[P2-MAINTENANCE] Naive DateTime**: Is `DateTime.Now` used instead of `DateTimeOffset.UtcNow`?

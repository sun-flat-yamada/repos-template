---
title: 'Coding Profile: C#'
description: Production implementation standards, architectural idioms, dependency
  hygiene, and testing guidelines for C#.
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
- csharp
alwaysApply: false
globs:
- '**/*.cs'
- '**/*.csproj'
- '**/*.sln'
---
# Coding Profile: C# (`coding-profile-csharp`)

## Target Standards
- **Standard Version**: .NET 8 / .NET 9+ (C# 12 / C# 13)
- **Primary Toolchain**: `dotnet build`, `dotnet test`, `dotnet format`, Roslyn Analyzers

---

## 🎯 Critical Engineering Safeguards (High-Impact Idioms)

### 1. Banning `async void` (Except UI Event Handlers)
- **Rule**: Never use `async void`. Exceptions thrown inside `async void` cannot be caught by callers and will terminate the process via the UnhandledException handler.
- **Anti-Pattern (Process Crasher)**:
  ```csharp
  // BAD: Crashes the entire ASP.NET Core process or worker if an exception occurs
  public async void ProcessMessageAsync(Message msg) {
      await SendAsync(msg);
  }
  ```
- **Resilient Idiom**:
  ```csharp
  // GOOD: Returns Task and allows caller to observe/await exceptions
  public async Task ProcessMessageAsync(Message msg, CancellationToken ct = default) {
      await SendAsync(msg, ct);
  }
  ```

### 2. Primary Constructor Parameter Capture Pitfalls
- **Rule**: In C# 12+ primary constructors for classes (`class Order(int id)`), primary constructor parameters are mutable captured state if assigned or read in methods, NOT readonly fields!
- **Idiom**: If immutability is desired, declare an explicit readonly property or use `record`:
  ```csharp
  public class Order(int id) {
      public int Id { get; } = id; // Immutable property
  }
  ```

### 3. LINQ Multiple Enumeration Defense
- **Rule**: Do not enumerate an `IEnumerable<T>` multiple times (e.g. `if (items.Any()) { Process(items.First()); }`). This triggers duplicate SQL queries or re-executes expensive computations.
- **Idiom**: Materialize with `.ToList()` or `.ToArray()` before multiple inspections.

### 4. Banned Antipatterns
- Blocking on asynchronous code (`task.Result`, `task.Wait()`). Triggers thread pool starvation and sync-context deadlocks.
- Using `DateTime.Now` instead of `DateTimeOffset.UtcNow`.

---
title: General Coding Rules
description: Universal coding conventions, defensive engineering practices, error
  management, and code hygiene.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- coding
- best-practices
- hygiene
alwaysApply: true
globs:
- '**/*'
---
# General Coding Rules (`coding-rules-general`)

These fundamental principles apply across all programming languages and components in this repository.

## 1. Core Engineering Principles
- **KISS (Keep It Simple, Stupid)**: Favor straightforward, obvious solutions over clever or heavily convoluted abstractions.
- **YAGNI (You Aren't Gonna Need It)**: Do not write speculative code or build plugin systems for hypothetical future requirements.
- **DRY (Don't Repeat Yourself)**: Eliminate duplicate logic, but balance against accidental coupling. Three occurrences warrant abstraction.
- **SOLID Principles**:
  - Single Responsibility: One cohesive purpose per class/function.
  - Open/Closed: Open for extension via interfaces, closed for modification.
  - Liskov Substitution: Subtypes must be substitutable for their base types.
  - Interface Segregation: Keep interfaces fine-grained and client-focused.
  - Dependency Inversion: Depend upon abstractions, not concrete implementations.

## 2. Test-Driven Development (TDD)
- When adding logic or fixing defects, first write failing tests demonstrating the desired behavior.
- Ensure all tests are deterministic, isolated, and fast.

## 3. Code Cleanliness & Readability
- Use intention-revealing variable and function names.
- Avoid magic numbers and hardcoded string constants; use named constants or enums.
- Keep function lengths concise (ideally under 40 lines).

---
title: 'Language Coding Rules: Go'
description: Language-specific style guidelines, static analysis requirements, and
  best practices for Go.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- language-rules
- go
alwaysApply: false
globs:
- '**/*.go'
- '**/go.mod'
- '**/go.sum'
---
# Language Coding Rules: Go (`coding-rules-go`)

## 1. Idiomatic Conventions & Simplicity
- Adhere to Effective Go and Go Code Review Comments.
- Single responsibility: keep functions focused. Return early to reduce nested `if/else` blocks.
- Package design: avoid utility packages (`util`, `common`). Structure packages by domain capability.

## 2. Error Handling & Concurrency
- Never ignore errors: always check `if err != nil` and propagate with context using `fmt.Errorf("...: %w", err)`.
- Use `errors.Is` for sentinel error comparison and `errors.As` for custom error struct inspection.
- Concurrency: Never leak goroutines. Pass `context.Context` to control cancellation and timeouts.
- Protect shared mutable state with `sync.Mutex` or `sync.RWMutex`, or prefer channel-based communication.

## 3. Tooling & Enforcement
- Run `golangci-lint run` in CI with strict linters enabled (`govet`, `errcheck`, `staticcheck`, `revive`).
- Enforce formatting using `gofmt` and `goimports`.

---
title: 'Coding Profile: Go'
description: Production implementation standards, architectural idioms, dependency
  hygiene, and testing guidelines for Go.
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
- go
alwaysApply: false
globs:
- '**/*.go'
- '**/go.mod'
- '**/go.sum'
---
# Coding Profile: Go (`coding-profile-go`)

## Target Standards
- **Standard Version**: Go 1.22 / Go 1.23+
- **Primary Toolchain**: `golangci-lint run`, `go test -race`, `gofmt`

---

## 🎯 Critical Engineering Safeguards (High-Impact Idioms)

### 1. Goroutine Lifecycle & Leak Defense
- **Rule**: Never spawn a goroutine without a deterministic cancellation signal (`context.Context`) and clean termination guarantee.
- **Anti-Pattern (Goroutine Leak)**:
  ```go
  // BAD: If receiver abandons or timeout occurs, sender blocks forever -> Goroutine Leak
  ch := make(chan int) // Unbuffered channel
  go func() {
      ch <- computeResult()
  }()
  ```
- **Resilient Idiom**:
  ```go
  // GOOD: Buffered channel or context-cancellation check
  ch := make(chan int, 1)
  go func() {
      select {
      case ch <- computeResult():
      case <-ctx.Done():
      }
  }()
  ```

### 2. HTTP Response Body Hygiene
- **Rule**: Always close `resp.Body` after verifying `err == nil`. Check `io.Copy(io.Discard, resp.Body)` before closing if reusing HTTP connections.
- **Example**:
  ```go
  resp, err := client.Do(req)
  if err != nil {
      return fmt.Errorf("http request: %w", err)
  }
  defer resp.Body.Close()
  ```

### 3. Error Wrapping & Inspection
- **Rule**: Use `fmt.Errorf("...: %w", err)` to wrap. NEVER compare errors with `==` unless comparing against sentinel values that are never wrapped; always use `errors.Is(err, ErrTarget)` and `errors.As(err, &target)`.

### 4. Lock Scope in Loops
- **Rule**: Avoid `defer mu.Unlock()` inside a loop. The defer statement only executes when the enclosing function returns, not at the end of the loop iteration!
- **Idiom**: Scope the lock inside an anonymous function or explicitly call `mu.Lock()` and `mu.Unlock()` within the iteration.

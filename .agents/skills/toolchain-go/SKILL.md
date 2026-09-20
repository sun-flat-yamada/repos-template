---
name: "toolchain-go"
description: "Executes Go development toolchains including go build, go test with race detection, golangci-lint, and gofmt formatting."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.go"
  - "**/go.mod"
  - "**/go.sum"
tags:
  - "skill"
  - "toolchain"
  - "go"
  - "build"
  - "test"
---
# Skill: Go Toolchain (`toolchain-go`)

## Instructions
1. **Module Download & Verification**:
   ```bash
   go mod download
   go mod verify
   ```
2. **Linting & Formatting**:
   ```bash
   gofmt -s -w .
   golangci-lint run
   ```
3. **Automated Testing with Race Detector**:
   ```bash
   go test -v -race -cover ./...
   ```

## Best Practices
- Always enable the `-race` flag during testing to prevent data races.
- Ensure all exported package identifiers have godoc comments.

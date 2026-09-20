---
name: "toolchain-python"
description: "Executes Python development workflows including pytest test suites, ruff linting/formatting, mypy typechecking, and uv dependency management."
category: "skill"
status: "active"
alwaysApply: false
globs:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/requirements*.txt"
  - "**/setup.py"
tags:
  - "skill"
  - "toolchain"
  - "python"
  - "build"
  - "test"
---
# Skill: Python Toolchain (`toolchain-python`)

## Instructions
1. **Environment & Dependency Sync**:
   ```bash
   uv sync
   # or: pip install -e ".[dev]"
   ```
2. **Linting & Formatting**:
   ```bash
   ruff check .
   ruff format --check .
   ```
3. **Static Type Checking**:
   ```bash
   mypy --strict .
   ```
4. **Automated Testing**:
   ```bash
   pytest -v --cov=. --cov-report=term-missing
   ```

## Best Practices
- Never bypass type annotations on public signatures.
- Ensure all tests run in an isolated virtual environment (`.venv`).

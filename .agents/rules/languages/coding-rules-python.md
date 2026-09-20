---
title: 'Language Coding Rules: Python'
description: Language-specific style guidelines, static analysis requirements, and
  best practices for Python.
category: rules
type: specification
status: active
date: 2026-09-20
updated: 2026-09-21
lang: en
tags:
- rules
- language-rules
- python
alwaysApply: false
globs:
- '**/*.py'
- '**/pyproject.toml'
- '**/requirements*.txt'
- '**/setup.py'
---
# Language Coding Rules: Python (`coding-rules-python`)

## 1. Type Strictness & Modern Syntax
- **Strict Typing**: All function and method definitions must include full argument and return type annotations.
- **Modern Python 3.10+ Syntaxes**:
  - Use pipe unions: `str | None` instead of `Optional[str]`.
  - Use standard container generics: `list[str]`, `dict[str, int]`, `tuple[int, ...]` instead of `typing.List`, `typing.Dict`.
- **Structured Data**: Use `@dataclass(frozen=True)` or `pydantic.BaseModel` for data transfer objects.

## 2. Robustness & Clean Code
- Never use mutable default parameters (`def fn(items=[])` is prohibited).
- Avoid bare `except:` or broad `except Exception:` without re-raising or detailed logging.
- Use context managers (`with` statements) for file handles, network sessions, and database connections.

## 3. Tooling & Enforcement
- Linter & Formatter: Enforce `ruff check .` and `ruff format --check .`.
- Static Type Checking: Enforce `mypy --strict .` in CI.
- Package Manager: Utilize `uv` or `poetry` with locked dependencies.
- Testing: Execute test suites using `pytest -v --cov=.`.

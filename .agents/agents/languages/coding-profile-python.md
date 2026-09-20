---
title: 'Coding Profile: Python'
description: Production implementation standards, architectural idioms, dependency
  hygiene, and testing guidelines for Python.
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
- python
alwaysApply: false
globs:
- '**/*.py'
- '**/pyproject.toml'
- '**/requirements*.txt'
- '**/setup.py'
---
# Coding Profile: Python (`coding-profile-python`)

## Target Standards
- **Standard Version**: Python 3.10+ (Targeting 3.11 / 3.12 / 3.13)
- **Primary Toolchain**: `ruff check`, `ruff format`, `mypy --strict`, `pytest`

---

## 🎯 Critical Engineering Safeguards (High-Impact Idioms)

### 1. Async Cancellation Safety & Resource Cleanup
- **Rule**: Every async resource acquisition (connection, lock, file) MUST be guarded with `async with` or `try...finally`.
- **Anti-Pattern (Silent Leak)**:
  ```python
  # BAD: If cancelled at await, session is never closed
  async def fetch_data(url: str) -> dict[str, Any]:
      session = aiohttp.ClientSession()
      res = await session.get(url)  # TaskCancelledError here leaks session
      await session.close()
      return await res.json()
  ```
- **Resilient Idiom**:
  ```python
  # GOOD: Guaranteed cleanup even under asyncio.CancelledError
  async def fetch_data(url: str) -> dict[str, Any]:
      async with aiohttp.ClientSession() as session:
          async with session.get(url) as res:
              return await res.json()
  ```

### 2. Exception Chaining & Traceback Preservation
- **Rule**: When transforming domain exceptions, ALWAYS use `from err` to preserve the root cause traceback. Never discard original context.
- **Example**:
  ```python
  # BAD: Destroys original stack trace
  except DatabaseError:
      raise RepositoryError("User lookup failed")

  # GOOD: Preserves cause for production debugging
  except DatabaseError as err:
      raise RepositoryError("User lookup failed") from err
  ```

### 3. Pydantic v2 Strict Validation & Immutability
- **Rule**: Use `BaseModel` with `model_config = ConfigDict(frozen=True, extra="forbid")` for domain models. Never bypass validation with `model_construct()` on untrusted external data.

### 4. Explicit Timezone Awareness
- **Rule**: Never use `datetime.datetime.now()` without timezone; it produces naive timestamps that crash when compared against UTC-aware values in databases.
- **Idiom**: Always use `datetime.datetime.now(datetime.timezone.utc)`.

### 5. Type Strictness & Banned Antipatterns
- Prohibit `Any` unless interfacing with dynamic C-extensions. Use `object` or generic type variables (`T`).
- Prohibit mutable default arguments (`def fn(items: list[str] = [])` -> `def fn(items: list[str] | None = None)`).

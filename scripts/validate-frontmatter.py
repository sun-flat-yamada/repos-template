#!/usr/bin/env python3
"""
scripts/validate-frontmatter.py
==============================================================================
Markdown YAML Front-Matter Linter & Validator
==============================================================================
Validates that all markdown (*.md) files in the repository have a valid,
well-formed YAML front-matter block conforming to docs/guides/front-matter-standards.md.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

try:
    import yaml
except ImportError:
    print("Error: 'yaml' module not found. Please install PyYAML to run this validator.")
    sys.exit(1)


def validate_markdown_frontmatter(file_path: Path) -> List[str]:
    errors: List[str] = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Failed to read file: {e}"]

    if not content.startswith("---"):
        return ["Missing front-matter opening delimiter ('---')"]

    parts = content.split("---", 2)
    if len(parts) < 3:
        return ["Malformed front-matter: missing closing delimiter ('---')"]

    fm_raw = parts[1]
    try:
        data = yaml.safe_load(fm_raw)
    except Exception as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(data, dict):
        return ["Front-matter content did not parse into a valid YAML mapping (dictionary)"]

    # SKILL.md adheres to Agent Skill Specification
    is_skill = "skills" in file_path.parts and file_path.name == "SKILL.md"
    if is_skill:
        if "name" not in data or not str(data["name"]).strip():
            errors.append("Missing or empty required field 'name' in SKILL front-matter")
        if "description" not in data or not str(data["description"]).strip():
            errors.append("Missing or empty required field 'description' in SKILL front-matter")
        if "tags" not in data or not isinstance(data["tags"], list) or len(data["tags"]) == 0:
            errors.append("Missing or invalid 'tags' list in SKILL front-matter")
    else:
        if "title" not in data or not str(data["title"]).strip():
            errors.append("Missing or empty required field 'title' in front-matter")
        if "description" not in data or not str(data["description"]).strip():
            errors.append("Missing or empty required field 'description' in front-matter")

    # Optional but standardized fields validation
    if "tags" in data and not isinstance(data["tags"], list):
        errors.append("Field 'tags' must be a list/array of strings")
    if "globs" in data and not isinstance(data["globs"], list):
        errors.append("Field 'globs' must be a list/array of glob strings")
    if "alwaysApply" in data and not isinstance(data["alwaysApply"], bool):
        errors.append("Field 'alwaysApply' must be a boolean (true/false)")

    return errors


def main() -> int:
    root = Path(".")
    total_files = 0
    passed_files = 0
    failures: List[Tuple[Path, List[str]]] = []

    for file_path in root.rglob("*.md"):
        if ".git" in file_path.parts:
            continue
        total_files += 1
        errs = validate_markdown_frontmatter(file_path)
        if errs:
            failures.append((file_path, errs))
        else:
            passed_files += 1

    print(f"Validated {total_files} markdown files.")
    if failures:
        print(f"\n[FAIL] Found {len(failures)} files with front-matter errors:")
        for path, errs in failures:
            print(f"\n- {path}:")
            for err in errs:
                print(f"    * {err}")
        return 1

    print(f"[PASS] All {passed_files} markdown files contain valid, high-quality YAML front-matter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

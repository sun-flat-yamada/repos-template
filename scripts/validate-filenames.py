#!/usr/bin/env python3
"""
scripts/validate-filenames.py
==============================================================================
Repository File Naming Convention Validator
==============================================================================
Enforces naming conventions across the repository, with special enforcement
for AI agent definitions (*.agent.md, prefix 'agent-' forbidden), rules,
workflows, skills, ADRs, and general files.

Supports full repository scanning or staged-only scanning (--staged).
Zero external dependencies: runs purely on Python 3.8+ standard libraries.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Ignored directories
IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    "dist",
    "build",
}

# Root-level uppercase markdown / standard files allowed
ALLOWED_ROOT_UPPERCASE = {
    "CHANGELOG.md",
    "CLAUDE.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "Makefile",
    "README.ja.md",
    "README.md",
    "SECURITY.md",
}

# Regex patterns for specific domains
AGENT_DEF_PATTERN = re.compile(r"^[a-z0-9-]+(?<!\.agent)\.agent\.md$")
RULE_DEF_PATTERN = re.compile(r"^[a-z0-9]+-rules-[a-z0-9-]+\.md$")
WORKFLOW_DEF_PATTERN = re.compile(r"^workflow-[a-z0-9-]+\.md$")
ADR_PATTERN = re.compile(r"^\d{4}-[a-z0-9-]+\.md$")
LANGUAGE_PROFILE_PATTERN = re.compile(r"^(coding|code-review)-profile-[a-z0-9-]+\.md$")
SKILL_DIR_PATTERN = re.compile(r"^[a-z0-9-]+$")


def get_staged_files(repo_root: Path) -> List[Path]:
    """Retrieve list of staged files via git diff."""
    try:
        output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=str(repo_root),
            text=True,
            encoding="utf-8",
        )
        files = [repo_root / line.strip() for line in output.splitlines() if line.strip()]
        return [f for f in files if f.is_file()]
    except Exception as err:
        print(f"[!] Warning: Unable to get staged files via git ({err}). Scanning full repository.")
        return get_all_files(repo_root)


def get_all_files(repo_root: Path) -> List[Path]:
    """Retrieve all files in repository excluding ignored directories."""
    matched: List[Path] = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            matched.append(Path(root) / f)
    return matched


def validate_file(file_path: Path, repo_root: Path) -> List[str]:
    """Validate a single file against naming conventions."""
    errors: List[str] = []
    try:
        rel_path = file_path.relative_to(repo_root)
    except ValueError:
        return errors

    parts = rel_path.parts
    filename = file_path.name

    # 1. No whitespace in any path component
    for part in parts:
        if " " in part:
            errors.append(f"{rel_path}: Contains whitespace characters in path component '{part}'.")

    # 2. Agent definition files (.agents/agents/*.agent.md)
    if len(parts) == 3 and parts[0] == ".agents" and parts[1] == "agents":
        # Direct children of .agents/agents/
        if filename.startswith("agent-"):
            errors.append(
                f"{rel_path}: Forbidden prefix 'agent-'. Agent definitions MUST use '*.agent.md' suffix instead (e.g. '{filename.replace('agent-', '').replace('.md', '.agent.md')}')."
            )
        elif not AGENT_DEF_PATTERN.match(filename):
            errors.append(
                f"{rel_path}: Agent definition must follow '<name>.agent.md' format using lowercase kebab-case."
            )

    # 3. Agent language profiles (.agents/agents/languages/*.md)
    elif len(parts) == 4 and parts[0] == ".agents" and parts[1] == "agents" and parts[2] == "languages":
        if not LANGUAGE_PROFILE_PATTERN.match(filename):
            errors.append(
                f"{rel_path}: Language profile must follow 'coding-profile-<lang>.md' or 'code-review-profile-<lang>.md'."
            )

    # 4. Rules (.agents/rules/*.md and .agents/rules/languages/*.md)
    elif parts[0] == ".agents" and parts[1] == "rules" and filename.endswith(".md"):
        if not RULE_DEF_PATTERN.match(filename):
            errors.append(
                f"{rel_path}: Rule file must follow '<category>-rules-<scope>.md' format (e.g. 'coding-rules-general.md')."
            )

    # 5. Workflows (.agents/workflows/*.md)
    elif parts[0] == ".agents" and parts[1] == "workflows" and filename.endswith(".md"):
        if not WORKFLOW_DEF_PATTERN.match(filename):
            errors.append(
                f"{rel_path}: Workflow file must follow 'workflow-<name>.md' format (e.g. 'workflow-spec-to-code.md')."
            )

    # 6. Skills (.agents/skills/<skill-dir>/SKILL.md)
    elif parts[0] == ".agents" and parts[1] == "skills":
        if len(parts) >= 3:
            skill_dir = parts[2]
            if not SKILL_DIR_PATTERN.match(skill_dir):
                errors.append(
                    f"{rel_path}: Skill directory name '{skill_dir}' must use lowercase kebab-case."
                )
        if len(parts) == 4 and parts[3] != "SKILL.md" and parts[3].endswith(".md"):
            # Markdown files inside skill root should normally be SKILL.md
            pass

    # 7. ADRs (docs/adr/*.md)
    elif len(parts) == 3 and parts[0] == "docs" and parts[1] == "adr" and filename.endswith(".md"):
        if filename != "template.md" and not ADR_PATTERN.match(filename):
            errors.append(
                f"{rel_path}: ADR file must follow 'NNNN-<kebab-case-slug>.md' format with 4-digit zero padding (e.g. '0001-init.md')."
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate repository file naming conventions."
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Validate only git staged files instead of the entire repository.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root directory (defaults to parent of scripts/).",
    )
    args = parser.parse_args()

    repo_root = args.root.resolve()
    if not repo_root.exists():
        print(f"[!] Repository root does not exist: {repo_root}", file=sys.stderr)
        return 1

    if args.staged:
        files_to_check = get_staged_files(repo_root)
        mode_str = "staged files"
    else:
        files_to_check = get_all_files(repo_root)
        mode_str = "all repository files"

    print(f"[*] Validating naming conventions across {len(files_to_check)} {mode_str}...")

    all_errors: List[str] = []
    for file_path in files_to_check:
        errs = validate_file(file_path, repo_root)
        all_errors.extend(errs)

    if all_errors:
        print(f"\n[X] Naming convention validation failed with {len(all_errors)} error(s):\n", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        print("\nPlease rename violating files according to `.agents/rules/naming-rules-general.md`.", file=sys.stderr)
        return 1

    print(f"[+] All {len(files_to_check)} files strictly comply with naming conventions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

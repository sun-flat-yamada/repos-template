#!/usr/bin/env python3
"""
scripts/apply-template.py
==============================================================================
GitHub Repository Template - Parameter Substitution & Verification Engine
==============================================================================
Substitutes placeholders formatted as {<UPPER_SNAKE_CASE>} throughout the
repository based on mappings defined in template.config.yaml or template.config.json.

Zero external dependencies: runs purely with Python 3.8+ standard libraries.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Default Directories & Files to skip from replacement
EXCLUDE_DIRS: Set[str] = {
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
    ".eggs",
    "*.egg-info",
}

# Binary and non-text extensions to skip
EXCLUDE_EXTS: Set[str] = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".webp",
    ".pdf",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".bin",
    ".tar",
    ".gz",
    ".zip",
    ".7z",
    ".pyc",
    ".pyo",
    ".pyd",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
}

# Regex to detect placeholders like {PROJECT_NAME}, {REPOSITORY_OWNER}, etc.
# Uses negative lookbehind (?<!\$) so Bash/Zsh variables like ${VAR} are not falsely matched.
PLACEHOLDER_PATTERN = re.compile(r"(?<!\$)\{([A-Z0-9_]{3,})\}")


def parse_simple_yaml(text: str) -> Dict[str, str]:
    """Parse basic YAML key: value pairs without external dependencies."""
    data: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            # Strip quotes if present
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            data[key] = val
    return data


def load_config(config_path: Path) -> Dict[str, str]:
    """Load configuration parameters from YAML or JSON."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    content = config_path.read_text(encoding="utf-8")
    if config_path.suffix.lower() == ".json":
        data = json.loads(content)
        return {str(k): str(v) for k, v in data.items()}
    else:
        # Try PyYAML if installed, otherwise use simple fallback
        try:
            import yaml  # type: ignore
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
        except ImportError:
            pass
        return parse_simple_yaml(content)


def should_skip_dir(dir_name: str) -> bool:
    return dir_name in EXCLUDE_DIRS


def should_skip_file(file_path: Path) -> bool:
    if file_path.suffix.lower() in EXCLUDE_EXTS:
        return True
    return False


def find_files(root: Path) -> List[Path]:
    """Recursively collect all candidate files in the repository."""
    candidates: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

        for fname in filenames:
            fpath = Path(dirpath) / fname
            if not should_skip_file(fpath):
                candidates.append(fpath)
    return candidates


def inspect_placeholders(root: Path, self_path: Path | None = None) -> Dict[Path, List[Tuple[int, str]]]:
    """Find all unresolved placeholders across candidate files."""
    results: Dict[Path, List[Tuple[int, str]]] = {}
    for file_path in find_files(root):
        if file_path.name in {"template.config.yaml", "template.config.json"}:
            continue
        if self_path and file_path.resolve() == self_path.resolve():
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        matches: List[Tuple[int, str]] = []
        for line_num, line in enumerate(content.splitlines(), start=1):
            found = PLACEHOLDER_PATTERN.findall(line)
            for m in found:
                matches.append((line_num, m))

        if matches:
            results[file_path] = matches
    return results


def apply_substitutions(
    root: Path,
    config: Dict[str, str],
    dry_run: bool = False,
    self_path: Path | None = None,
) -> int:
    """Apply dictionary substitutions across all repository files."""
    files = find_files(root)
    modified_count = 0

    # Build regex substitution table
    patterns = {re.compile(r"\{" + re.escape(k) + r"\}"): v for k, v in config.items()}

    print(f"[*] Scanning {len(files)} files with {len(config)} parameter mappings...")

    for file_path in files:
        # Don't overwrite the config file or this script during normal run
        if file_path.name in {"template.config.yaml", "template.config.json"}:
            continue
        if self_path and file_path.resolve() == self_path.resolve():
            continue

        try:
            original = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        modified = original
        changes_in_file = 0
        for pattern, replacement in patterns.items():
            modified, count = pattern.subn(replacement, modified)
            changes_in_file += count

        if changes_in_file > 0:
            modified_count += 1
            rel_path = file_path.relative_to(root)
            if dry_run:
                print(f"  [DRY-RUN] {rel_path} ({changes_in_file} substitutions)")
            else:
                file_path.write_text(modified, encoding="utf-8")
                print(f"  [UPDATED] {rel_path} ({changes_in_file} substitutions)")

    return modified_count


def finalize_cleanup(root: Path) -> None:
    """Optionally remove template parameter files and initial setup engine."""
    targets = [
        root / "template.config.yaml",
        root / "template.config.json",
        root / "scripts" / "setup.ps1",
        root / "scripts" / "setup.sh",
    ]
    for t in targets:
        if t.exists():
            t.unlink()
            print(f"  [REMOVED] {t.name}")
    print("[+] Repository finalized. Template engine files cleaned up.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GitHub Repository Template - Substitution and Verification Engine"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=None,
        help="Path to configuration YAML or JSON (default: template.config.yaml or template.config.json)",
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Show substitutions without writing changes to disk",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for unresolved placeholders and exit with code 1 if found",
    )
    parser.add_argument(
        "--finalize",
        action="store_true",
        help="Cleanup template configuration files after successful application",
    )

    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent

    # Check mode
    if args.check:
        print(f"[*] Checking for unresolved placeholders in: {root}")
        found = inspect_placeholders(root, self_path=Path(__file__).resolve())
        total_placeholders = sum(len(items) for items in found.values())

        if total_placeholders > 0:
            print(f"[!] Found {total_placeholders} unresolved placeholder(s) across {len(found)} file(s):")
            for fpath, items in found.items():
                rel = fpath.relative_to(root)
                for line_num, placeholder in items:
                    print(f"    {rel}:{line_num} -> {{{placeholder}}}")
            return 1
        else:
            print("[+] Zero unresolved placeholders found. Clean verification!")
            return 0

    # Determine config file
    config_path = args.config
    if config_path is None:
        yaml_cand = root / "template.config.yaml"
        json_cand = root / "template.config.json"
        if yaml_cand.exists():
            config_path = yaml_cand
        elif json_cand.exists():
            config_path = json_cand
        else:
            print("[ERROR] Neither template.config.yaml nor template.config.json found.")
            return 1

    print(f"[*] Loading config from: {config_path}")
    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        return 1

    print(f"[*] Applying parameters ({'DRY-RUN' if args.dry_run else 'APPLY'} mode)...")
    self_path = Path(__file__).resolve()
    count = apply_substitutions(root, config, dry_run=args.dry_run, self_path=self_path)

    if args.dry_run:
        print(f"[+] Dry run completed. {count} file(s) would be modified.")
    else:
        print(f"[+] Application completed. {count} file(s) updated.")

    if args.finalize and not args.dry_run:
        print("[*] Finalizing template...")
        finalize_cleanup(root)

    return 0


if __name__ == "__main__":
    sys.exit(main())

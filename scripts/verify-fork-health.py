#!/usr/bin/env python3
"""
scripts/verify-fork-health.py
==============================================================================
Fork Health Verifier
==============================================================================
Read-only checks that a fork (or mirror copy) of this template is ready for
the dual-branch operation described in docs/guides/fork-operations-guide.md:

  1. an `upstream` remote is configured
  2. the current branch is a customization branch (not main, not detached)
  3. the working tree is clean
  4. local `main` is a pure mirror of `upstream/main` (fast-forward only)
  5. no unresolved template placeholders remain

The script never writes to the repository and never touches the network; run
`git fetch upstream` first so that `upstream/main` is current.

Exit code: 0 when no check failed (1 with --strict if any warning), else 1.
Zero external dependencies: Python 3.8+ standard library only.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"

UPSTREAM_REMOTE = "upstream"
MIRROR_BRANCH = "main"
UPSTREAM_REF = f"{UPSTREAM_REMOTE}/{MIRROR_BRANCH}"
PLACEHOLDER_PATTERN = re.compile(r"(?<!\$)\{([A-Z0-9_]{3,})\}")
# git grep -E has no lookbehind, so it pre-filters and PLACEHOLDER_PATTERN decides.
PLACEHOLDER_PREFILTER = r"\{[A-Z0-9_]{3,}\}"
MAX_PLACEHOLDER_SAMPLES = 5


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    message: str


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=False
    )


def check_upstream_remote(repo: Path) -> CheckResult:
    name = "upstream-remote"
    done = run_git(repo, "remote", "get-url", UPSTREAM_REMOTE)
    if done.returncode != 0:
        return CheckResult(name, FAIL, f"remote '{UPSTREAM_REMOTE}' is not configured")
    return CheckResult(name, PASS, f"{UPSTREAM_REMOTE} -> {done.stdout.strip()}")


def check_current_branch(repo: Path) -> CheckResult:
    name = "current-branch"
    done = run_git(repo, "symbolic-ref", "--short", "-q", "HEAD")
    branch = done.stdout.strip()
    if done.returncode != 0 or not branch:
        return CheckResult(name, FAIL, "HEAD is detached; check out a customization branch")
    if branch == MIRROR_BRANCH:
        return CheckResult(
            name, FAIL, f"'{MIRROR_BRANCH}' is the upstream mirror; commit on a customization branch"
        )
    return CheckResult(name, PASS, f"on '{branch}'")


def check_clean_worktree(repo: Path) -> CheckResult:
    name = "clean-worktree"
    done = run_git(repo, "status", "--porcelain")
    if done.returncode != 0:
        return CheckResult(name, FAIL, f"git status failed: {done.stderr.strip()}")
    if done.stdout.strip():
        count = len(done.stdout.strip().splitlines())
        return CheckResult(name, FAIL, f"{count} uncommitted or untracked change(s)")
    return CheckResult(name, PASS, "working tree is clean")


def check_main_mirrors_upstream(repo: Path) -> CheckResult:
    name = "main-mirror"
    if run_git(repo, "rev-parse", "--verify", "-q", f"refs/remotes/{UPSTREAM_REF}").returncode != 0:
        return CheckResult(name, FAIL, f"{UPSTREAM_REF} not found; run 'git fetch {UPSTREAM_REMOTE}'")
    if run_git(repo, "rev-parse", "--verify", "-q", f"refs/heads/{MIRROR_BRANCH}").returncode != 0:
        return CheckResult(name, FAIL, f"local branch '{MIRROR_BRANCH}' does not exist")
    local = run_git(repo, "rev-parse", MIRROR_BRANCH).stdout.strip()
    remote = run_git(repo, "rev-parse", UPSTREAM_REF).stdout.strip()
    if local == remote:
        return CheckResult(name, PASS, f"{MIRROR_BRANCH} matches {UPSTREAM_REF}")
    is_ancestor = run_git(repo, "merge-base", "--is-ancestor", MIRROR_BRANCH, UPSTREAM_REF)
    if is_ancestor.returncode == 0:
        return CheckResult(
            name, WARN, f"{MIRROR_BRANCH} is behind {UPSTREAM_REF}; a fast-forward is possible"
        )
    return CheckResult(
        name, FAIL, f"{MIRROR_BRANCH} has commits that are not in {UPSTREAM_REF}; it cannot fast-forward"
    )


def check_placeholders(repo: Path) -> CheckResult:
    name = "placeholders"
    done = run_git(repo, "grep", "-I", "-n", "-E", PLACEHOLDER_PREFILTER, "--", ".")
    hits: List[str] = []
    for line in done.stdout.splitlines():
        path, _, rest = line.partition(":")
        _, _, text = rest.partition(":")
        if PLACEHOLDER_PATTERN.search(text):
            hits.append(path)
    if not hits:
        return CheckResult(name, PASS, "no unresolved placeholders")
    files = sorted(set(hits))
    sample = ", ".join(files[:MAX_PLACEHOLDER_SAMPLES])
    return CheckResult(
        name, WARN, f"unresolved placeholders in {len(files)} file(s): {sample}"
    )


def run_checks(repo: Path) -> List[CheckResult]:
    return [
        check_upstream_remote(repo),
        check_current_branch(repo),
        check_clean_worktree(repo),
        check_main_mirrors_upstream(repo),
        check_placeholders(repo),
    ]


def exit_code(results: List[CheckResult], strict: bool) -> int:
    blocking = {FAIL, WARN} if strict else {FAIL}
    return 1 if any(r.status in blocking for r in results) else 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Verify the health of a template fork (read-only).")
    parser.add_argument("--repo", default=".", help="Path to the fork checkout (default: .)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    if run_git(repo, "rev-parse", "--git-dir").returncode != 0:
        print(f"[ERROR] not a git repository: {repo}")
        return 1

    results = run_checks(repo)
    for r in results:
        print(f"[{r.status}] {r.name}: {r.message}")
    return exit_code(results, args.strict)


if __name__ == "__main__":
    sys.exit(main())

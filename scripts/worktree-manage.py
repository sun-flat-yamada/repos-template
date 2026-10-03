#!/usr/bin/env python3
"""
scripts/worktree-manage.py
==============================================================================
Sibling Git Worktree Manager for Multi-Agent Concurrent Workflows
==============================================================================
Worktrees live NEXT TO the repository (`../<repo>-worktrees/<branch-slug>`),
never inside it, so scanners, test runners, and `git status` stay clean.

    python scripts/worktree-manage.py add <branch> [base-branch]   # default base: main
    python scripts/worktree-manage.py list
    python scripts/worktree-manage.py clean <branch>               # plain `git worktree remove`
    python scripts/worktree-manage.py remove <branch>              # checked, forced removal

`remove` is the ONLY sanctioned way to force-remove a worktree (ADR-0004). It refuses
unless nothing can be lost: sibling directory, not the main or current worktree,
not locked, no tracked changes, no untracked files except git-ignored ones, and
HEAD already contained in `origin/<branch>` or `origin/<base>`. Anything else is
reported and left for a human; raw `git worktree remove --force` stays C-HITL-03.

Zero external dependencies: runs on Python 3.8+ standard libraries.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

DEFAULT_BASE_BRANCH = "main"
REMOTE = "origin"
BRANCH_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
REPO_ROOT = Path(__file__).resolve().parent.parent

USAGE = """\
Usage:
  python scripts/worktree-manage.py add <branch> [base-branch]
  python scripts/worktree-manage.py list
  python scripts/worktree-manage.py clean <branch>
  python scripts/worktree-manage.py remove <branch>

Example:
  python scripts/worktree-manage.py add feat/42-export-cost-centers
"""


class RemovalBlocked(Exception):
    """Raised when a forced removal could lose work; carries the human-readable reasons."""

    def __init__(self, reasons: List[str]):
        super().__init__("; ".join(reasons))
        self.reasons = reasons


def run_git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=str(repo), text=True, stderr=subprocess.STDOUT).strip()


def git_succeeds(repo: Path, *args: str) -> bool:
    return subprocess.run(["git", *args], cwd=str(repo), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def to_slug(branch: str) -> str:
    return re.sub(r"[/\\:]", "-", branch)


def validate_branch_name(branch: str) -> None:
    if not BRANCH_PATTERN.match(branch) or ".." in branch:
        raise ValueError(f"Unsafe or invalid branch name: {branch!r}")


def worktrees_dir(repo: Path) -> Path:
    return repo.parent / f"{repo.name}-worktrees"


def add_worktree(repo: Path, branch: str, base: str = DEFAULT_BASE_BRANCH) -> Path:
    validate_branch_name(branch)
    validate_branch_name(base)
    target = worktrees_dir(repo) / to_slug(branch)
    if target.exists():
        raise FileExistsError(f"Target worktree directory already exists: {target}")
    try:
        run_git(repo, "fetch", REMOTE, base)
    except subprocess.CalledProcessError as err:
        print(f"[!] Could not fetch {REMOTE}/{base}; using the local ref. ({err.output.strip()})")
    target.parent.mkdir(parents=True, exist_ok=True)
    run_git(repo, "worktree", "add", str(target), "-b", branch, f"{REMOTE}/{base}")
    return target


def clean_worktree(repo: Path, branch: str) -> None:
    validate_branch_name(branch)
    target = worktrees_dir(repo) / to_slug(branch)
    run_git(repo, "worktree", "remove", str(target))
    run_git(repo, "worktree", "prune")
    delete_merged_branch(repo, branch)


def delete_merged_branch(repo: Path, branch: str) -> None:
    try:
        run_git(repo, "branch", "-d", branch)
    except subprocess.CalledProcessError:
        print(f'[i] Local branch "{branch}" was kept (not fully merged yet). A human may run: git branch -D "{branch}"')


def parse_worktrees(repo: Path) -> List[dict]:
    """`git worktree list --porcelain` as dicts with path, branch (or None), locked; main worktree first."""
    entries: List[dict] = []
    for block in run_git(repo, "worktree", "list", "--porcelain").split("\n\n"):
        entry: dict = {"locked": False, "branch": None}
        for line in block.splitlines():
            key, _, value = line.partition(" ")
            if key == "worktree":
                entry["path"] = Path(value).resolve()
            elif key == "branch":
                entry["branch"] = value[len("refs/heads/"):]
            elif key == "locked":
                entry["locked"] = True
        if "path" in entry:
            entries.append(entry)
    return entries


def is_within(child: Path, parent: Path) -> bool:
    return child == parent or parent in child.parents


def is_pushed(target: Path, branch: str) -> bool:
    """HEAD is contained in origin/<branch> or in origin/<default base> (merged, remote branch deleted)."""
    for ref in (f"refs/remotes/{REMOTE}/{branch}", f"refs/remotes/{REMOTE}/{DEFAULT_BASE_BRANCH}"):
        if git_succeeds(target, "rev-parse", "--verify", "--quiet", ref) and git_succeeds(target, "merge-base", "--is-ancestor", "HEAD", ref):
            return True
    return False


def removal_blockers(repo: Path, branch: str, cwd: Optional[Path] = None) -> List[str]:
    """Reasons a forced removal of the sibling worktree for `branch` could lose work (empty = safe)."""
    validate_branch_name(branch)
    target = (worktrees_dir(repo) / to_slug(branch)).resolve()
    worktrees = parse_worktrees(repo)
    entry = next((w for w in worktrees if w["path"] == target), None)
    if entry is None or entry["path"] == worktrees[0]["path"]:
        return [f"no sibling worktree for {branch!r} at {target}"]
    reasons: List[str] = []
    if entry["branch"] != branch:
        reasons.append(f"worktree has {entry['branch'] or 'a detached HEAD'} checked out, not {branch!r}")
    if entry["locked"]:
        reasons.append("worktree is locked")
    if is_within((cwd or Path.cwd()).resolve(), target):
        reasons.append("worktree is the current working directory")
    if reasons or not target.is_dir():
        return reasons or ["worktree directory is missing; run `git worktree prune`"]
    status = run_git(target, "status", "--porcelain", "--untracked-files=all").splitlines()
    if any(not line.startswith("??") for line in status):
        reasons.append("uncommitted tracked changes")
    if any(line.startswith("??") for line in status):
        reasons.append("untracked files that are not git-ignored")
    if not is_pushed(target, branch):
        reasons.append(f"HEAD is not pushed ({REMOTE}/{branch}) or merged ({REMOTE}/{DEFAULT_BASE_BRANCH})")
    return reasons


def remove_worktree(repo: Path, branch: str) -> None:
    reasons = removal_blockers(repo, branch)
    if reasons:
        raise RemovalBlocked(reasons)
    target = worktrees_dir(repo) / to_slug(branch)
    run_git(repo, "worktree", "remove", "--force", str(target))  # safe: checked above (ADR-0004)
    run_git(repo, "worktree", "prune")
    delete_merged_branch(repo, branch)


def main(argv: list) -> int:
    command = argv[0] if argv else ""
    try:
        if command == "add" and len(argv) in (2, 3):
            target = add_worktree(REPO_ROOT, argv[1], *argv[2:])
            print(f"[OK] Worktree ready: {target}\n     Next: cd \"{target}\"")
        elif command == "list" and len(argv) == 1:
            print(run_git(REPO_ROOT, "worktree", "list"))
        elif command == "clean" and len(argv) == 2:
            clean_worktree(REPO_ROOT, argv[1])
            print("[OK] Cleanup complete.")
        elif command == "remove" and len(argv) == 2:
            remove_worktree(REPO_ROOT, argv[1])
            print("[OK] Worktree removed.")
        else:
            print(USAGE, file=sys.stderr if command else sys.stdout)
            return 1 if command else 0
    except RemovalBlocked as err:
        print("[X] Not removed (a human must decide):", *[f"\n    - {r}" for r in err.reasons], file=sys.stderr)
        return 2
    except (ValueError, FileExistsError) as err:
        print(f"[X] {err}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as err:
        print(f"[X] git failed: {err.output.strip()}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

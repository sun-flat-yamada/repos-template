#!/usr/bin/env python3
"""
tests/test-worktree-manage.py
==============================================================================
Unit tests for scripts/worktree-manage.py `remove` (ADR-0003): a forced removal
is allowed only when nothing can be lost. Uses real temporary git repositories.

    python tests/test-worktree-manage.py -v
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "worktree-manage.py"
BRANCH = "feat/14-demo"


def load_module():
    spec = importlib.util.spec_from_file_location("worktree_manage", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


wm = load_module()


def git(cwd: Path, *args: str) -> str:
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    return subprocess.check_output(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", *args],
        cwd=str(cwd), text=True, stderr=subprocess.STDOUT, env=env,
    ).strip()


class RemoveWorktreeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name).resolve()
        self.origin = root / "origin.git"
        self.repo = root / "repo"
        git(root, "init", "--bare", "-b", "main", str(self.origin))
        git(root, "clone", str(self.origin), str(self.repo))
        (self.repo / ".gitignore").write_text("build/\n")
        (self.repo / "a.txt").write_text("a\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "init")
        git(self.repo, "push", "-u", "origin", "main")
        self.target = wm.add_worktree(self.repo, BRANCH)

    def commit_in_worktree(self, name: str = "b.txt") -> None:
        (self.target / name).write_text("b\n")
        git(self.target, "add", name)
        git(self.target, "commit", "-m", "work")

    def push(self) -> None:
        git(self.target, "push", "-u", "origin", BRANCH)

    def reasons(self):
        return wm.removal_blockers(self.repo, BRANCH)

    def test_pushed_clean_worktree_is_removable(self):
        self.commit_in_worktree()
        self.push()
        self.assertEqual(self.reasons(), [])

    def test_ignored_untracked_files_do_not_block(self):
        self.commit_in_worktree()
        self.push()
        (self.target / "build").mkdir()
        (self.target / "build" / "out.o").write_text("x")
        self.assertEqual(self.reasons(), [])
        wm.remove_worktree(self.repo, BRANCH)
        self.assertFalse(self.target.exists())

    def test_unpushed_commit_blocks(self):
        self.commit_in_worktree()
        self.assertTrue(any("not pushed" in r for r in self.reasons()))

    def test_commit_after_push_blocks(self):
        self.commit_in_worktree()
        self.push()
        self.commit_in_worktree("c.txt")
        self.assertTrue(any("not pushed" in r for r in self.reasons()))

    def test_branch_merged_into_origin_main_is_removable_even_if_remote_branch_is_gone(self):
        self.commit_in_worktree()
        self.push()
        git(self.repo, "fetch", "origin")
        git(self.repo, "push", "origin", f"origin/{BRANCH}:refs/heads/main")
        git(self.repo, "push", "origin", "--delete", BRANCH)
        git(self.repo, "fetch", "--prune", "origin")
        self.assertEqual(self.reasons(), [])

    def test_tracked_modification_blocks(self):
        self.push()
        (self.target / "a.txt").write_text("changed\n")
        self.assertTrue(any("uncommitted" in r for r in self.reasons()))

    def test_staged_change_blocks(self):
        self.push()
        (self.target / "new.txt").write_text("n\n")
        git(self.target, "add", "new.txt")
        self.assertTrue(any("uncommitted" in r for r in self.reasons()))

    def test_untracked_non_ignored_file_blocks(self):
        self.push()
        (self.target / "notes.txt").write_text("n\n")
        self.assertTrue(any("untracked" in r for r in self.reasons()))

    def test_locked_worktree_blocks(self):
        self.push()
        git(self.repo, "worktree", "lock", str(self.target))
        self.assertTrue(any("locked" in r for r in self.reasons()))

    def test_current_worktree_blocks(self):
        self.push()
        previous = Path.cwd()
        os.chdir(self.target / "build" if (self.target / "build").exists() else self.target)
        self.addCleanup(os.chdir, previous)
        self.assertTrue(any("current" in r for r in self.reasons()))

    def test_unknown_worktree_blocks(self):
        self.assertTrue(wm.removal_blockers(self.repo, "feat/99-missing"))

    def test_main_worktree_is_never_removable(self):
        self.assertTrue(wm.removal_blockers(self.repo, "main"))

    def test_unsafe_branch_name_is_rejected(self):
        for name in ("../escape", "feat/../../x", "-rf", "a b"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    wm.removal_blockers(self.repo, name)

    def test_remove_refuses_when_blocked_and_keeps_directory(self):
        self.commit_in_worktree()
        with self.assertRaises(wm.RemovalBlocked):
            wm.remove_worktree(self.repo, BRANCH)
        self.assertTrue(self.target.exists())

    def test_remove_deletes_worktree_and_merged_branch(self):
        self.commit_in_worktree()
        self.push()
        git(self.repo, "fetch", "origin")
        git(self.repo, "push", "origin", f"{BRANCH}:main")
        git(self.repo, "pull", "--ff-only", "origin", "main")
        wm.remove_worktree(self.repo, BRANCH)
        self.assertFalse(self.target.exists())
        self.assertNotIn(BRANCH, git(self.repo, "branch", "--list"))


if __name__ == "__main__":
    unittest.main(argv=sys.argv)

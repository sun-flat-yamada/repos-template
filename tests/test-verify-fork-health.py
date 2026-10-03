#!/usr/bin/env python3
"""
tests/test-verify-fork-health.py
==============================================================================
Unit tests for scripts/verify-fork-health.py.

Run directly (the hyphenated file name is not importable by unittest discovery):

    python tests/test-verify-fork-health.py -v

Uses only local git repositories in a temp directory; no network access.
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
SCRIPT_PATH = REPO_ROOT / "scripts" / "verify-fork-health.py"

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}


def load_module():
    spec = importlib.util.spec_from_file_location("verify_fork_health", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


health = load_module()


def git(cwd: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", *args], cwd=cwd, env=GIT_ENV, check=True, capture_output=True, text=True
    )
    return done.stdout.strip()


def commit_file(repo: Path, name: str, text: str) -> None:
    (repo / name).write_text(text, encoding="utf-8")
    git(repo, "add", name)
    git(repo, "commit", "-m", f"chore: add {name}")


class ForkRepoCase(unittest.TestCase):
    """A bare 'upstream' and a clone acting as the fork, both under a temp dir."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.upstream = base / "upstream.git"
        self.seed = base / "seed"
        self.fork = base / "fork"
        git(base, "init", "--bare", "-b", "main", str(self.upstream))
        git(base, "clone", str(self.upstream), str(self.seed))
        git(self.seed, "checkout", "-b", "main")
        commit_file(self.seed, "README.md", "# base\n")
        git(self.seed, "push", "origin", "main")
        git(base, "clone", str(self.upstream), str(self.fork))
        git(self.fork, "checkout", "-b", "fork/custom")

    def add_upstream_remote(self):
        git(self.fork, "remote", "add", "upstream", str(self.upstream))
        git(self.fork, "fetch", "upstream")

    def advance_upstream(self):
        commit_file(self.seed, "new.txt", "new\n")
        git(self.seed, "push", "origin", "main")
        git(self.fork, "fetch", "upstream")


class UpstreamRemoteTests(ForkRepoCase):
    def test_fails_without_upstream_remote(self):
        self.assertEqual(health.check_upstream_remote(self.fork).status, health.FAIL)

    def test_passes_with_upstream_remote(self):
        self.add_upstream_remote()
        self.assertEqual(health.check_upstream_remote(self.fork).status, health.PASS)


class CurrentBranchTests(ForkRepoCase):
    def test_passes_on_custom_branch(self):
        self.assertEqual(health.check_current_branch(self.fork).status, health.PASS)

    def test_fails_on_main(self):
        git(self.fork, "checkout", "main")
        self.assertEqual(health.check_current_branch(self.fork).status, health.FAIL)

    def test_fails_on_detached_head(self):
        git(self.fork, "checkout", "--detach")
        self.assertEqual(health.check_current_branch(self.fork).status, health.FAIL)


class CleanWorktreeTests(ForkRepoCase):
    def test_passes_when_clean(self):
        self.assertEqual(health.check_clean_worktree(self.fork).status, health.PASS)

    def test_fails_with_untracked_file(self):
        (self.fork / "scratch.txt").write_text("x", encoding="utf-8")
        self.assertEqual(health.check_clean_worktree(self.fork).status, health.FAIL)

    def test_fails_with_modified_file(self):
        (self.fork / "README.md").write_text("changed\n", encoding="utf-8")
        self.assertEqual(health.check_clean_worktree(self.fork).status, health.FAIL)


class MainMirrorTests(ForkRepoCase):
    def test_fails_without_upstream_ref(self):
        self.assertEqual(health.check_main_mirrors_upstream(self.fork).status, health.FAIL)

    def test_passes_when_in_sync(self):
        self.add_upstream_remote()
        self.assertEqual(health.check_main_mirrors_upstream(self.fork).status, health.PASS)

    def test_warns_when_behind_but_fast_forwardable(self):
        self.add_upstream_remote()
        self.advance_upstream()
        self.assertEqual(health.check_main_mirrors_upstream(self.fork).status, health.WARN)

    def test_fails_when_main_has_fork_only_commits(self):
        self.add_upstream_remote()
        git(self.fork, "checkout", "main")
        commit_file(self.fork, "local.txt", "local\n")
        git(self.fork, "checkout", "fork/custom")
        self.assertEqual(health.check_main_mirrors_upstream(self.fork).status, health.FAIL)


class PlaceholderTests(ForkRepoCase):
    def test_passes_without_placeholders(self):
        self.assertEqual(health.check_placeholders(self.fork).status, health.PASS)

    def test_warns_on_unresolved_placeholder(self):
        commit_file(self.fork, "doc.md", "Name: {PROJECT_NAME}\n")
        self.assertEqual(health.check_placeholders(self.fork).status, health.WARN)

    def test_ignores_shell_variables(self):
        commit_file(self.fork, "run.sh", "echo ${PROJECT_NAME}\n")
        self.assertEqual(health.check_placeholders(self.fork).status, health.PASS)


class ExitCodeTests(unittest.TestCase):
    def results(self, *statuses):
        return [health.CheckResult("c", s, "m") for s in statuses]

    def test_pass_and_warn_exit_zero(self):
        self.assertEqual(health.exit_code(self.results(health.PASS, health.WARN), strict=False), 0)

    def test_fail_exits_one(self):
        self.assertEqual(health.exit_code(self.results(health.PASS, health.FAIL), strict=False), 1)

    def test_strict_turns_warn_into_failure(self):
        self.assertEqual(health.exit_code(self.results(health.WARN), strict=True), 1)


if __name__ == "__main__":
    unittest.main()

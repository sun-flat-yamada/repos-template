#!/usr/bin/env python3
"""
tests/test-sync-upstream.py
==============================================================================
Unit tests for scripts/sync-upstream.py.

Run directly (the hyphenated file name is not importable by unittest discovery):

    python tests/test-sync-upstream.py -v

Uses only local git repositories as the "upstream"; no network access.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "sync-upstream.py"


def load_module():
    spec = importlib.util.spec_from_file_location("sync_upstream", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


sync = load_module()


def git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=str(cwd),
        text=True,
    ).strip()


class SyncUpstreamTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = Path(self._tmp.name)
        self.upstream = tmp / "upstream"
        self.project = tmp / "project"
        self.upstream.mkdir()
        self.project.mkdir()
        git(self.upstream, "init", "-q", "-b", "main")
        self.write_upstream("a.md", "alpha\n")
        self.write_upstream("dir/b.md", "bravo\n")
        self.commit_upstream("init")
        self.manifest = self.project / "upstream" / "src.json"
        self.manifest.parent.mkdir(parents=True)
        self.manifest.write_text(
            json.dumps(
                {
                    "repo": str(self.upstream),
                    "synced_commit": None,
                    "files": [
                        {"source": "a.md", "adapted": "out/a.md"},
                        {"source": "dir/b.md", "adapted": "out/b.md"},
                    ],
                }
            ),
            encoding="utf-8",
        )

    def write_upstream(self, rel: str, text: str) -> None:
        path = self.upstream / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def commit_upstream(self, msg: str) -> str:
        git(self.upstream, "add", "-A")
        git(self.upstream, "commit", "-q", "-m", msg)
        return git(self.upstream, "rev-parse", "HEAD")

    def snapshot(self, rel: str) -> Path:
        return self.manifest.parent / "src" / rel

    def test_first_update_creates_snapshots_and_records_commit(self) -> None:
        head = git(self.upstream, "rev-parse", "HEAD")
        report = sync.run_update(self.manifest)
        self.assertEqual(self.snapshot("a.md").read_text(encoding="utf-8"), "alpha\n")
        self.assertEqual(self.snapshot("dir/b.md").read_text(encoding="utf-8"), "bravo\n")
        self.assertEqual(json.loads(self.manifest.read_text(encoding="utf-8"))["synced_commit"], head)
        self.assertEqual({e.status for e in report.entries}, {"added"})

    def test_check_is_clean_right_after_update(self) -> None:
        sync.run_update(self.manifest)
        report = sync.run_check(self.manifest)
        self.assertFalse(report.has_changes)

    def test_check_detects_modified_and_does_not_write(self) -> None:
        sync.run_update(self.manifest)
        self.write_upstream("a.md", "alpha2\n")
        self.commit_upstream("change a")
        report = sync.run_check(self.manifest)
        self.assertTrue(report.has_changes)
        statuses = {e.source: e.status for e in report.entries}
        self.assertEqual(statuses, {"a.md": "modified", "dir/b.md": "unchanged"})
        self.assertEqual(self.snapshot("a.md").read_text(encoding="utf-8"), "alpha\n")

    def test_update_refreshes_snapshot_and_reports_diff(self) -> None:
        sync.run_update(self.manifest)
        self.write_upstream("a.md", "alpha2\n")
        new_head = self.commit_upstream("change a")
        report = sync.run_update(self.manifest)
        modified = [e for e in report.entries if e.status == "modified"]
        self.assertEqual(len(modified), 1)
        self.assertIn("-alpha", modified[0].diff)
        self.assertIn("+alpha2", modified[0].diff)
        self.assertEqual(self.snapshot("a.md").read_text(encoding="utf-8"), "alpha2\n")
        self.assertEqual(json.loads(self.manifest.read_text(encoding="utf-8"))["synced_commit"], new_head)

    def test_dry_run_update_writes_nothing(self) -> None:
        report = sync.run_update(self.manifest, dry_run=True)
        self.assertTrue(report.has_changes)
        self.assertFalse(self.snapshot("a.md").exists())
        self.assertIsNone(json.loads(self.manifest.read_text(encoding="utf-8"))["synced_commit"])

    def test_missing_upstream_file_is_reported_and_snapshot_kept(self) -> None:
        sync.run_update(self.manifest)
        (self.upstream / "a.md").unlink()
        self.commit_upstream("remove a")
        report = sync.run_update(self.manifest)
        statuses = {e.source: e.status for e in report.entries}
        self.assertEqual(statuses["a.md"], "missing")
        self.assertTrue(self.snapshot("a.md").exists())

    def test_rejects_path_traversal_in_manifest(self) -> None:
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        data["files"].append({"source": "../evil.md", "adapted": "out/evil.md"})
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError):
            sync.run_check(self.manifest)

    def test_rejects_non_https_and_non_local_repo_schemes(self) -> None:
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        data["repo"] = "ext::sh -c 'echo pwned'"
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError):
            sync.run_check(self.manifest)


class MultiManifestTests(unittest.TestCase):
    """Every manifest in a directory is checked, and one failure does not stop the rest."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = Path(self._tmp.name)
        self.manifest_dir = tmp / "project" / "upstream"
        self.manifest_dir.mkdir(parents=True)
        self.upstreams = {}
        for name in ("first", "second"):
            repo = tmp / name
            repo.mkdir()
            git(repo, "init", "-q", "-b", "main")
            (repo / "a.md").write_text(f"{name}\n", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "init")
            self.upstreams[name] = repo
            self.write_manifest(name, str(repo))

    def write_manifest(self, name: str, repo: str) -> Path:
        path = self.manifest_dir / f"{name}.json"
        data = {"repo": repo, "synced_commit": None, "files": [{"source": "a.md", "adapted": f"out/{name}.md"}]}
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_discover_manifests_returns_sorted_json_files_only(self) -> None:
        (self.manifest_dir / "notes.txt").write_text("x", encoding="utf-8")
        (self.manifest_dir / "first").mkdir()
        found = sync.discover_manifests(self.manifest_dir)
        self.assertEqual([p.name for p in found], ["first.json", "second.json"])

    def test_discover_manifests_fails_when_none_found(self) -> None:
        with self.assertRaises(ValueError):
            sync.discover_manifests(self.manifest_dir / "empty")

    def test_run_all_update_then_check_covers_every_manifest(self) -> None:
        manifests = sync.discover_manifests(self.manifest_dir)
        sync.run_all(manifests, write=True)
        results = sync.run_all(manifests, write=False)
        self.assertEqual([r.manifest.name for r in results], ["first.json", "second.json"])
        self.assertTrue(all(r.error is None and not r.report.has_changes for r in results))

    def test_run_all_isolates_a_failing_manifest(self) -> None:
        self.write_manifest("broken", str(self.manifest_dir / "does-not-exist"))
        results = sync.run_all(sync.discover_manifests(self.manifest_dir), write=False)
        by_name = {r.manifest.name: r for r in results}
        self.assertIsNotNone(by_name["broken.json"].error)
        self.assertIsNone(by_name["first.json"].error)
        self.assertTrue(by_name["second.json"].report.has_changes)

    def test_exit_code_reports_error_over_changes(self) -> None:
        manifests = sync.discover_manifests(self.manifest_dir)
        self.assertEqual(sync.exit_code(sync.run_all(manifests, write=False)), 1)
        sync.run_all(manifests, write=True)
        self.assertEqual(sync.exit_code(sync.run_all(manifests, write=False)), 0)
        self.write_manifest("broken", str(self.manifest_dir / "does-not-exist"))
        self.assertEqual(sync.exit_code(sync.run_all(sync.discover_manifests(self.manifest_dir), write=False)), 2)


if __name__ == "__main__":
    unittest.main()

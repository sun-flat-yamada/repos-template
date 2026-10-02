#!/usr/bin/env python3
"""
scripts/sync-upstream.py
==============================================================================
Upstream Snapshot Synchronizer
==============================================================================
Tracks files that were adopted from an external ("upstream") repository.

For every upstream file listed in a manifest, a verbatim snapshot is kept under
`<manifest-dir>/<manifest-stem>/<source-path>`. The files actually used by this
repository (the "adapted" files) are hand-maintained derivatives of those
snapshots. Because the adapted files diverge on purpose, they are never
overwritten. Instead:

    check   Compare upstream HEAD with the snapshots. Writes nothing.
            Exit code 1 when anything changed (usable from CI / cron).
    update  Refresh the snapshots, record the upstream commit in the manifest,
            and print the diff of each changed file. Port that diff into the
            adapted file by hand (or with an AI agent).

Manifest (JSON):
    {
      "repo": "https://github.com/<owner>/<name>",   # https URL or local path
      "synced_commit": "<sha or null>",
      "files": [{"source": "<path in upstream>", "adapted": "<path here>"}]
    }

Zero external dependencies: runs on Python 3.8+ standard libraries.
See docs/guides/upstream-sync-guide.md.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

DEFAULT_MANIFEST = Path(".agents/upstream/github-copilot-dashboard.json")

STATUS_ADDED = "added"
STATUS_MODIFIED = "modified"
STATUS_UNCHANGED = "unchanged"
STATUS_MISSING = "missing"
CHANGED_STATUSES = frozenset({STATUS_ADDED, STATUS_MODIFIED, STATUS_MISSING})


@dataclass
class Entry:
    source: str
    adapted: str
    status: str
    diff: str = ""


@dataclass
class Report:
    repo: str
    old_commit: str
    new_commit: str
    entries: List[Entry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(e.status in CHANGED_STATUSES for e in self.entries)


def load_manifest(manifest_path: Path) -> dict:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    repo = str(data.get("repo", ""))
    if not (repo.startswith("https://") or Path(repo).is_dir()):
        raise ValueError(f"Manifest 'repo' must be an https:// URL or an existing local directory: {repo!r}")
    for item in data.get("files", []):
        for key in ("source", "adapted"):
            _check_relative(str(item.get(key, "")), key)
    return data


def _check_relative(value: str, key: str) -> None:
    parts = Path(value).parts
    if not value or Path(value).is_absolute() or ".." in parts:
        raise ValueError(f"Manifest '{key}' must be a safe relative path: {value!r}")


def snapshot_root(manifest_path: Path) -> Path:
    return manifest_path.parent / manifest_path.stem


def fetch_upstream(repo: str, dest: Path) -> str:
    """Shallow-clone `repo` into `dest` and return the HEAD commit SHA."""
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
    subprocess.run(
        ["git", "clone", "--quiet", "--depth", "1", "--", repo, str(dest)],
        check=True,
        env=env,
    )
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(dest), text=True).strip()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _diff(old: str, new: str, label: str) -> str:
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"snapshot/{label}",
            tofile=f"upstream/{label}",
        )
    )


def _compare(manifest_path: Path, data: dict, upstream_dir: Path, new_commit: str, write: bool) -> Report:
    snaps = snapshot_root(manifest_path)
    report = Report(data["repo"], data.get("synced_commit") or "", new_commit)
    for item in data["files"]:
        source, adapted = item["source"], item["adapted"]
        up_file, snap_file = upstream_dir / source, snaps / source
        if not up_file.is_file():
            report.entries.append(Entry(source, adapted, STATUS_MISSING))
            continue
        new_text = _read(up_file)
        if not snap_file.is_file():
            report.entries.append(Entry(source, adapted, STATUS_ADDED))
        elif _read(snap_file) == new_text:
            report.entries.append(Entry(source, adapted, STATUS_UNCHANGED))
            continue
        else:
            report.entries.append(Entry(source, adapted, STATUS_MODIFIED, _diff(_read(snap_file), new_text, source)))
        if write:
            snap_file.parent.mkdir(parents=True, exist_ok=True)
            snap_file.write_text(new_text, encoding="utf-8", newline="")
    return report


def _run(manifest_path: Path, write: bool) -> Report:
    data = load_manifest(manifest_path)
    with tempfile.TemporaryDirectory() as tmp:
        upstream_dir = Path(tmp) / "upstream"
        new_commit = fetch_upstream(data["repo"], upstream_dir)
        report = _compare(manifest_path, data, upstream_dir, new_commit, write)
    if write:
        data["synced_commit"] = new_commit
        manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def run_check(manifest_path: Path) -> Report:
    return _run(manifest_path, write=False)


def run_update(manifest_path: Path, dry_run: bool = False) -> Report:
    return _run(manifest_path, write=not dry_run)


def print_report(report: Report, show_diff: bool) -> None:
    print(f"[*] Upstream: {report.repo}")
    print(f"    synced commit : {report.old_commit or '(never)'}")
    print(f"    upstream HEAD : {report.new_commit}")
    for entry in report.entries:
        print(f"  [{entry.status:9}] {entry.source}  ->  adapted: {entry.adapted}")
        if show_diff and entry.diff:
            print(entry.diff)
    if report.has_changes:
        print("\n[!] Port the changes above into the adapted files "
              "(see docs/guides/upstream-sync-guide.md).")
    else:
        print("\n[OK] Snapshots match upstream.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Track and refresh files adopted from an upstream repository.")
    parser.add_argument("command", choices=["check", "update"])
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--dry-run", action="store_true", help="update: show the report without writing files.")
    args = parser.parse_args()

    if args.command == "check":
        report = run_check(args.manifest)
        print_report(report, show_diff=False)
        return 1 if report.has_changes else 0
    report = run_update(args.manifest, dry_run=args.dry_run)
    print_report(report, show_diff=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

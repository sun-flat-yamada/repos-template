#!/usr/bin/env python3
"""
tests/test-validate-frontmatter.py
==============================================================================
Unit tests for scripts/validate-frontmatter.py.

Run directly (the hyphenated file name is not importable by unittest discovery):

    python tests/test-validate-frontmatter.py -v

Requires PyYAML, like the validator itself.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate-frontmatter.py"

VALID_FRONT_MATTER = '---\ntitle: "Guide"\ndescription: "What this guide covers."\n---\n\n# Guide\n'
NO_FRONT_MATTER = "## Description\n\nBody text.\n"
MISSING_TITLE = '---\ndescription: "No title here."\n---\n\n# Body\n'


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_frontmatter", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class ValidateMarkdownTests(unittest.TestCase):
    """Front matter is required unless GitHub or an AI tool owns the file format."""

    def validate(self, rel_path: str, content: str):
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "document.md"
            file_path.write_text(content, encoding="utf-8")
            return validator.validate_markdown_frontmatter(file_path, Path(rel_path))

    def test_valid_front_matter_passes(self):
        self.assertEqual(self.validate("docs/guides/guide.md", VALID_FRONT_MATTER), [])

    def test_regular_documents_require_front_matter(self):
        errors = self.validate("docs/guides/guide.md", NO_FRONT_MATTER)
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing front-matter", errors[0])

    def test_pull_request_template_may_omit_front_matter(self):
        self.assertEqual(self.validate(".github/PULL_REQUEST_TEMPLATE.md", NO_FRONT_MATTER), [])

    def test_optional_files_are_validated_when_front_matter_is_present(self):
        errors = self.validate("README.md", MISSING_TITLE)
        self.assertTrue(any("'title'" in error for error in errors))

    def test_front_matter_requirement_by_path(self):
        cases = {
            ".github/PULL_REQUEST_TEMPLATE.md": False,
            "README.md": False,
            "CLAUDE.md": False,
            "docs/README.md": True,
            "docs/adr/0001-adopt-ai-agent-permission-policy.md": True,
            ".agents/rules/coding-rules-general.md": True,
        }
        for rel_path, required in cases.items():
            with self.subTest(path=rel_path):
                self.assertEqual(validator.frontmatter_required(Path(rel_path)), required)


class UpstreamSnapshotTests(unittest.TestCase):
    def test_snapshot_paths_are_exempt(self) -> None:
        self.assertTrue(validator.is_upstream_snapshot(Path(".agents/upstream/x/.agents/rules/a.md")))
        self.assertFalse(validator.is_upstream_snapshot(Path(".agents/rules/a.md")))


class RepositoryTests(unittest.TestCase):
    """Every markdown file shipped in the repository passes the validator."""

    def test_repository_markdown_passes(self):
        for file_path in sorted(REPO_ROOT.rglob("*.md")):
            rel_path = file_path.relative_to(REPO_ROOT)
            if ".git" in rel_path.parts or validator.is_upstream_snapshot(rel_path):
                continue
            with self.subTest(path=rel_path.as_posix()):
                self.assertEqual(validator.validate_markdown_frontmatter(file_path, rel_path), [])


if __name__ == "__main__":
    unittest.main(argv=sys.argv)

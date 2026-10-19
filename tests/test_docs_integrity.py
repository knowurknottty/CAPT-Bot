"""Regression tests for the public documentation integrity check."""
import tempfile
import unittest
from pathlib import Path

from scripts.check_docs import check


class DocumentationIntegrityTests(unittest.TestCase):
    def make_root(self, readme: str, page: str) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "docs").mkdir()
        (root / "README.md").write_text(readme, encoding="utf-8")
        (root / "docs" / "guide.md").write_text(page, encoding="utf-8")
        return root

    def test_valid_local_anchor(self):
        root = self.make_root("[Guide](docs/guide.md#read-me)\n", "# Read me\n")
        failures, scanned, links = check(root)
        self.assertEqual(failures, [])
        self.assertEqual((scanned, links), (2, 1))

    def test_missing_anchor_is_failure(self):
        root = self.make_root("[Guide](docs/guide.md#does-not-exist)\n", "# Read me\n")
        failures, _, _ = check(root)
        self.assertTrue(any("missing anchor" in problem for problem in failures))

    def test_missing_file_is_failure(self):
        root = self.make_root("[Missing](docs/404.md)\n", "# Read me\n")
        failures, _, _ = check(root)
        self.assertTrue(any("missing link destination" in problem for problem in failures))

    def test_unclosed_fence_is_failure(self):
        root = self.make_root("# Entry\n", chr(96) * 3 + "python\nprint(1)\n")
        failures, _, _ = check(root)
        self.assertTrue(any("unclosed Markdown fence" in problem for problem in failures))

    def test_code_fence_links_are_ignored(self):
        root = self.make_root(chr(96) * 3 + "markdown\n[Fake](nothing.md)\n" + chr(96) * 3 + "\n", "# Guide\n")
        failures, _, links = check(root)
        self.assertEqual(failures, [])
        self.assertEqual(links, 0)

    def test_traversal_rejected(self):
        root = self.make_root("[Outside](../outside.txt)\n", "# Guide\n")
        failures, _, _ = check(root)
        self.assertTrue(any("escapes repository" in problem for problem in failures))


if __name__ == "__main__":
    unittest.main()

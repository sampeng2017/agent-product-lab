from __future__ import annotations

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from residuecheck.cli import main
from residuecheck.core import Limits, SnapshotError, snapshot


class ResidueCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(self, *arguments: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(list(arguments))
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_reports_created_modified_and_removed_ignored_files(self) -> None:
        (self.root / ".gitignore").write_text("*.cache\n", encoding="utf-8")
        (self.root / "modified.cache").write_text("before", encoding="utf-8")
        (self.root / "removed.cache").write_text("before", encoding="utf-8")
        script = (
            "from pathlib import Path; "
            "Path('created.cache').write_text('new'); "
            "Path('modified.cache').write_text('after'); "
            "Path('removed.cache').unlink()"
        )
        exit_code, stdout, stderr = self.run_cli(
            "--root", str(self.root), "--", sys.executable, "-c", script
        )
        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        self.assertIn("CREATED created.cache", stdout)
        self.assertIn("MODIFIED modified.cache", stdout)
        self.assertIn("REMOVED removed.cache", stdout)
        self.assertIn("3 changes (1 created, 1 modified, 1 removed)", stdout)
        self.assertIn("Inspected: 3 entries and 20 bytes before; 3 entries and 16 bytes after", stdout)

    def test_clean_command_passes_and_excluded_prefix_is_not_hashed(self) -> None:
        (self.root / "kept.txt").write_text("stable", encoding="utf-8")
        excluded = self.root / "vendor"
        excluded.mkdir()
        (excluded / "large.bin").write_bytes(b"x" * 20)
        script = "from pathlib import Path; Path('vendor/large.bin').write_bytes(b'y' * 30)"
        exit_code, stdout, _ = self.run_cli(
            "--root", str(self.root), "--exclude", "vendor", "--max-file-bytes", "6",
            "--", sys.executable, "-c", script,
        )
        self.assertEqual(exit_code, 0)
        self.assertIn("Command: passed", stdout)
        self.assertIn("Result: clean\n", stdout)
        self.assertIn("Inspected: 1 entry and 6 bytes before; 1 entry and 6 bytes after", stdout)

    def test_preflight_bounds_prevent_command_execution(self) -> None:
        (self.root / "too-large.bin").write_bytes(b"12345")
        marker = self.root / "ran"
        exit_code, _, stderr = self.run_cli(
            "--root", str(self.root), "--max-file-bytes", "4", "--",
            sys.executable, "-c", "from pathlib import Path; Path('ran').touch()",
        )
        self.assertEqual(exit_code, 2)
        self.assertIn("file size limit exceeded", stderr)
        self.assertFalse(marker.exists())

    def test_entry_and_total_byte_bounds_are_explicit(self) -> None:
        (self.root / "a").write_text("12", encoding="utf-8")
        (self.root / "b").write_text("34", encoding="utf-8")
        with self.assertRaisesRegex(SnapshotError, "entry limit exceeded"):
            snapshot(self.root, exclusions=(), limits=Limits(max_entries=1))
        with self.assertRaisesRegex(SnapshotError, "total byte limit exceeded"):
            snapshot(self.root, exclusions=(), limits=Limits(max_total_bytes=3))

    def test_change_output_is_bounded_with_exact_overflow(self) -> None:
        script = (
            "from pathlib import Path; "
            "[Path(f'{index}.tmp').touch() for index in range(4)]"
        )
        exit_code, stdout, _ = self.run_cli(
            "--root", str(self.root), "--max-changes", "2", "--",
            sys.executable, "-c", script,
        )
        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.count("CREATED "), 2)
        self.assertIn("4 changes (4 created, 0 modified, 0 removed); 2 more not shown", stdout)

    def test_command_failure_is_reported_even_when_tree_is_clean(self) -> None:
        exit_code, stdout, _ = self.run_cli(
            "--root", str(self.root), "--", sys.executable, "-c", "raise SystemExit(7)"
        )
        self.assertEqual(exit_code, 1)
        self.assertIn("Command: failed (exit 7)", stdout)
        self.assertIn("Result: clean", stdout)

    def test_single_change_uses_singular_summary(self) -> None:
        exit_code, stdout, _ = self.run_cli(
            "--root", str(self.root), "--", sys.executable, "-c",
            "from pathlib import Path; Path('created').touch()",
        )
        self.assertEqual(exit_code, 1)
        self.assertIn("Result: 1 change (1 created, 0 modified, 0 removed)", stdout)

    def test_rejects_unsafe_exclusions_and_does_not_follow_directory_symlinks(self) -> None:
        exit_code, _, stderr = self.run_cli(
            "--root", str(self.root), "--exclude", "../outside", "--", sys.executable, "-c", ""
        )
        self.assertEqual(exit_code, 2)
        self.assertIn("invalid exclusion", stderr)
        outside = self.root.parent / f"{self.root.name}-outside"
        outside.mkdir()
        self.addCleanup(lambda: outside.rmdir())
        (self.root / "link").symlink_to(outside, target_is_directory=True)
        result = snapshot(self.root, exclusions=(), limits=Limits())
        self.assertIn("link", result.fingerprints)


if __name__ == "__main__":
    unittest.main()

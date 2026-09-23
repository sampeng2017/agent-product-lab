from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from grammarcheck.cli import main
from grammarcheck.core import InspectionError, check_sources, parse_target


class GrammarCheckTests(unittest.TestCase):
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

    def test_compatible_sources_are_sorted_deduplicated_and_counted(self) -> None:
        package = self.root / "src" / "example"
        package.mkdir(parents=True)
        (package / "z.py").write_text("answer = 42\n", encoding="utf-8")
        (package / "a.py").write_text("def ok():\n    return True\n", encoding="utf-8")

        exit_code, stdout, stderr = self.run_cli(
            "--root", str(self.root), "--target", "3.10", "src", "src/example/a.py"
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")
        self.assertLess(stdout.index("PASS src/example/a.py"), stdout.index("PASS src/example/z.py"))
        self.assertIn("2 compatible, 0 incompatible, 2 files", stdout)

    def test_reports_all_target_grammar_and_compiler_failures(self) -> None:
        source = self.root / "source"
        source.mkdir()
        (source / "new.py").write_text("match value:\n    case 1: pass\n", encoding="utf-8")
        (source / "scope.py").write_text("return 42\n", encoding="utf-8")

        exit_code, stdout, stderr = self.run_cli(
            "--root", str(self.root), "--target", "3.9", "source"
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        self.assertIn("INCOMPATIBLE source/new.py:2:17", stdout)
        self.assertIn("INCOMPATIBLE source/scope.py:1:1: 'return' outside function", stdout)
        self.assertIn("0 compatible, 2 incompatible, 2 files", stdout)

    def test_rejects_unsafe_missing_empty_and_symlink_sources(self) -> None:
        with self.assertRaisesRegex(InspectionError, "safe relative path"):
            check_sources(self.root, ["../outside"], (3, 10))
        with self.assertRaisesRegex(InspectionError, "not found"):
            check_sources(self.root, ["missing"], (3, 10))
        empty = self.root / "empty"
        empty.mkdir()
        with self.assertRaisesRegex(InspectionError, "contain no .py"):
            check_sources(self.root, ["empty"], (3, 10))
        real = self.root / "real.py"
        real.write_text("pass\n", encoding="utf-8")
        link = self.root / "link.py"
        try:
            link.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are unavailable")
        with self.assertRaisesRegex(InspectionError, "cannot be a symlink"):
            check_sources(self.root, ["link.py"], (3, 10))

    def test_bounds_and_invalid_targets_are_setup_errors(self) -> None:
        (self.root / "one.py").write_text("pass\n", encoding="utf-8")
        (self.root / "two.py").write_text("pass\n", encoding="utf-8")
        with self.assertRaisesRegex(InspectionError, "exceeds 1 files"):
            check_sources(self.root, ["."], (3, 10), max_files=1)
        with self.assertRaisesRegex(InspectionError, "per-file limit is 2"):
            check_sources(self.root, ["one.py"], (3, 10), max_file_bytes=2)
        with self.assertRaisesRegex(InspectionError, "target must use"):
            parse_target("310")
        exit_code, stdout, stderr = self.run_cli("--root", str(self.root), "one.py")
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("--target is required", stderr)


if __name__ == "__main__":
    unittest.main()

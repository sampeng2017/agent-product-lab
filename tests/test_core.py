from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from proofrun.core import assess_receipts, git_state, load_receipts, run_check, run_suite
from proofrun.manifest import load_manifest, select_checks


class ProofRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_successful_check_produces_valid_receipt(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        exit_code, receipt = run_check(
            name="smoke",
            command=[sys.executable, "-c", "print('ok')"],
            cwd=self.root,
            store=store,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(load_receipts(store), [receipt])
        assessed = assess_receipts(
            [receipt], current=git_state(self.root), max_age_hours=24
        )
        self.assertEqual(assessed[0]["state"], "valid")

    def test_working_tree_change_makes_receipt_stale(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        _, receipt = run_check(
            name="smoke",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )
        (self.root / "new.py").write_text("print('changed')\n", encoding="utf-8")

        assessed = assess_receipts(
            [receipt], current=git_state(self.root), max_age_hours=24
        )
        self.assertEqual(assessed[0]["state"], "stale")
        self.assertIn("working tree changed", assessed[0]["reasons"])

    def test_failed_or_expired_receipt_is_stale(self) -> None:
        old = datetime.now(timezone.utc) - timedelta(hours=48)
        current = git_state(self.root)
        receipt = {
            "name": "lint",
            "started_at": old.isoformat(),
            "exit_code": 1,
            "git": {
                "available": current.available,
                "head": current.head,
                "fingerprint": current.fingerprint,
            },
        }

        assessed = assess_receipts([receipt], current=current, max_age_hours=24)
        self.assertEqual(assessed[0]["state"], "stale")
        self.assertEqual(assessed[0]["reasons"], ["failed", "expired"])

    def test_manifest_load_and_selection(self) -> None:
        manifest = self.root / "proofrun.toml"
        manifest.write_text(
            """
[checks.unit]
command = ["python3", "-c", "print('unit')"]

[checks.lint]
command = ["python3", "-c", "print('lint')"]
""".strip()
            + "\n",
            encoding="utf-8",
        )

        checks = load_manifest(manifest)
        selected = select_checks(checks, ["lint"])

        self.assertEqual([check.name for check in checks], ["unit", "lint"])
        self.assertEqual([check.name for check in selected], ["lint"])
        self.assertEqual(selected[0].command, ("python3", "-c", "print('lint')"))

    def test_run_suite_records_each_check_and_stops_on_fail_fast(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        manifest = self.root / "proofrun.toml"
        manifest.write_text(
            f"""
[checks.fail]
command = ["{sys.executable}", "-c", "import sys; sys.exit(5)"]

[checks.pass]
command = ["{sys.executable}", "-c", "print('ok')"]
""".strip()
            + "\n",
            encoding="utf-8",
        )

        exit_code, results = run_suite(
            load_manifest(manifest),
            cwd=self.root,
            store=store,
            fail_fast=True,
        )

        self.assertEqual(exit_code, 5)
        self.assertEqual([item["name"] for item in results], ["fail"])
        self.assertEqual(load_receipts(store)[0]["name"], "fail")

    def test_select_checks_rejects_unknown_names(self) -> None:
        manifest = self.root / "proofrun.toml"
        manifest.write_text(
            """
[checks.unit]
command = ["python3", "-c", "print('unit')"]
""".strip()
            + "\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "unknown checks: lint"):
            select_checks(load_manifest(manifest), ["lint"])


if __name__ == "__main__":
    unittest.main()

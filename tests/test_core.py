from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from proofrun.core import assess_receipts, git_state, load_receipts, run_check


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


if __name__ == "__main__":
    unittest.main()

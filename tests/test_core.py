from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path

from proofrun.cli import main
from proofrun.core import (
    assess_receipts,
    audit_receipts,
    git_state,
    load_receipts,
    receipt_digest,
    run_check,
    run_suite,
)
from proofrun.manifest import load_manifest, select_checks
from proofrun.report import render_markdown_report


class ProofRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "proofrun@example.com"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "ProofRun Tests"],
            cwd=self.root,
            check=True,
        )

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
        self.assertEqual(assessed[0]["working_tree_paths"]["tracked"], [])
        self.assertEqual(assessed[0]["working_tree_paths"]["untracked"], ["new.py"])

    def test_status_reports_changed_tracked_and_untracked_paths(self) -> None:
        tracked = self.root / "tracked.py"
        tracked.write_text("print('v1')\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.py"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.root, check=True)

        store = self.root / ".proofrun" / "receipts.jsonl"
        _, receipt = run_check(
            name="smoke",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )

        tracked.write_text("print('v2')\n", encoding="utf-8")
        (self.root / "scratch.txt").write_text("hello\n", encoding="utf-8")

        assessed = assess_receipts(
            [receipt], current=git_state(self.root), max_age_hours=24
        )
        self.assertEqual(assessed[0]["working_tree_paths"]["tracked"], ["tracked.py"])
        self.assertEqual(assessed[0]["working_tree_paths"]["untracked"], ["scratch.txt"])

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

    def test_legacy_receipt_without_path_details_stays_readable(self) -> None:
        current = git_state(self.root)
        receipt = {
            "name": "lint",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "exit_code": 0,
            "git": {
                "available": current.available,
                "head": current.head,
                "fingerprint": "old-fingerprint",
            },
        }

        assessed = assess_receipts([receipt], current=current, max_age_hours=24)
        self.assertEqual(assessed[0]["reasons"], ["working tree changed"])
        self.assertEqual(
            assessed[0]["working_tree_paths"],
            {"tracked": [], "untracked": []},
        )

    def test_receipts_are_sealed_and_linked(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        _, first = run_check(
            name="first",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )
        _, second = run_check(
            name="second",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )

        self.assertEqual(first["schema_version"], 3)
        self.assertIsNone(first["previous_hash"])
        self.assertEqual(first["receipt_hash"], receipt_digest(first))
        self.assertEqual(second["previous_hash"], receipt_digest(first))
        self.assertEqual(second["receipt_hash"], receipt_digest(second))
        self.assertEqual(
            [item["state"] for item in audit_receipts([first, second])],
            ["valid", "valid"],
        )

    def test_tampering_breaks_chain_and_invalidates_downstream_proof(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        _, first = run_check(
            name="first",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )
        _, second = run_check(
            name="second",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )
        first["exit_code"] = 9

        audited = audit_receipts([first, second])
        assessed = assess_receipts(
            [first, second], current=git_state(self.root), max_age_hours=24
        )

        self.assertEqual([item["state"] for item in audited], ["invalid", "invalid"])
        self.assertIn("receipt hash mismatch", audited[0]["issues"])
        self.assertIn("previous receipt link mismatch", audited[1]["issues"])
        self.assertIn("receipt chain invalid", assessed[1]["reasons"])

    def test_new_receipt_seals_the_end_of_a_legacy_store(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        legacy = {
            "schema_version": 2,
            "id": "legacy",
            "name": "old",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "exit_code": 0,
            "git": {},
        }
        store.parent.mkdir(parents=True)
        store.write_text(f"{json.dumps(legacy)}\n", encoding="utf-8")

        _, receipt = run_check(
            name="new",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )

        self.assertEqual(receipt["previous_hash"], receipt_digest(legacy))
        self.assertEqual(
            [item["state"] for item in audit_receipts(load_receipts(store))],
            ["unsealed", "valid"],
        )

    def test_audit_cli_returns_failure_and_json_for_tampered_store(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        run_check(
            name="smoke",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )
        receipts = load_receipts(store)
        receipts[0]["exit_code"] = 3
        store.write_text(
            "".join(f"{json.dumps(receipt)}\n" for receipt in receipts),
            encoding="utf-8",
        )

        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(["--store", str(store), "audit", "--json"])

        summary = json.loads(output.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(summary["state"], "invalid")
        self.assertEqual(summary["invalid_count"], 1)
        self.assertEqual(summary["receipts"][0]["issues"], ["receipt hash mismatch"])

    def test_markdown_report_contains_status_metadata_and_changed_paths(self) -> None:
        tracked = self.root / "tracked.py"
        tracked.write_text("print('v1')\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.py"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.root, check=True)
        store = self.root / ".proofrun" / "receipts.jsonl"
        _, receipt = run_check(
            name="unit",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )
        tracked.write_text("print('v2')\n", encoding="utf-8")
        (self.root / "scratch.md").write_text("notes\n", encoding="utf-8")
        now = datetime.fromisoformat(receipt["started_at"]) + timedelta(hours=1)

        report = render_markdown_report(
            [receipt],
            current=git_state(self.root),
            max_age_hours=24,
            now=now,
        )

        self.assertIn("# ProofRun verification report", report)
        self.assertIn("- Checks: 0/1 currently valid", report)
        self.assertIn("- Receipt chain: VALID", report)
        self.assertIn("### `unit`", report)
        self.assertIn("- Status: **STALE** — working tree changed", report)
        self.assertIn(f"- Receipt: `{receipt['id']}`", report)
        self.assertIn("- Invalidating tracked paths: `tracked.py`", report)
        self.assertIn("- Invalidating untracked paths: `scratch.md`", report)
        self.assertEqual(
            report,
            render_markdown_report(
                [receipt],
                current=git_state(self.root),
                max_age_hours=24,
                now=now,
            ),
        )

    def test_report_cli_writes_file_and_fails_for_invalid_chain(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        run_check(
            name="smoke",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )
        receipts = load_receipts(store)
        receipts[0]["exit_code"] = 3
        store.write_text(
            "".join(f"{json.dumps(receipt)}\n" for receipt in receipts),
            encoding="utf-8",
        )
        output_path = self.root / "proof.md"
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main(
                [
                    "--store",
                    str(store),
                    "report",
                    "--output",
                    str(output_path),
                ]
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("wrote Markdown report", output.getvalue())
        report = output_path.read_text(encoding="utf-8")
        self.assertIn("- Receipt chain: INVALID", report)
        self.assertIn("receipt chain invalid, failed", report)

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

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor, wait as wait_for_futures
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import proofrun.core
from proofrun.cli import main
from proofrun.core import (
    CheckDefinition,
    append_receipt,
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
from proofrun.scaffold import (
    apply_scaffold_plan,
    detect_project_preset,
    plan_repository_initialization,
)


class ProofRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        subprocess.run(
            ["git", "init", "-q", "--initial-branch=main"],
            cwd=self.root,
            check=True,
        )
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
        self.assertEqual(receipt["command_exit_code"], 0)
        self.assertFalse(receipt["repository_mutation"]["detected"])
        self.assertEqual(receipt["git_before"], receipt["git"])
        assessed = assess_receipts(
            [receipt], current=git_state(self.root), max_age_hours=24
        )
        self.assertEqual(assessed[0]["state"], "valid")

    def test_git_state_uses_one_status_scan_for_untracked_files(self) -> None:
        tracked = self.root / "tracked.py"
        tracked.write_text("committed\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.py"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.root, check=True)
        unusual = self.root / "line\nbreak.txt"
        unusual.write_text("untracked\n", encoding="utf-8")

        with patch("proofrun.core._git", wraps=proofrun.core._git) as git:
            state = git_state(self.root)

        self.assertEqual(git.call_count, 1)
        self.assertEqual(
            git.call_args.args[1:],
            (
                "status",
                "--porcelain=v2",
                "--branch",
                "--untracked-files=all",
                "-z",
            ),
        )
        self.assertTrue(state.dirty)
        self.assertEqual(state.branch, "main")
        self.assertEqual(state.tracked_changes, {})
        self.assertEqual(set(state.untracked_files), {"line\nbreak.txt"})

    def test_git_state_handles_staged_rename_and_detached_head(self) -> None:
        original = self.root / "before name.txt"
        original.write_text("same content\n", encoding="utf-8")
        subprocess.run(["git", "add", original.name], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "mv", original.name, "after name.txt"],
            cwd=self.root,
            check=True,
        )

        renamed = git_state(self.root)

        self.assertEqual(set(renamed.tracked_changes), {"after name.txt"})
        subprocess.run(["git", "commit", "-qm", "rename"], cwd=self.root, check=True)
        subprocess.run(["git", "checkout", "-q", "--detach"], cwd=self.root, check=True)

        detached = git_state(self.root)

        self.assertIsNone(detached.branch)
        self.assertFalse(detached.dirty)

    def test_git_state_batches_tracked_diffs_without_changing_digests(self) -> None:
        paths = ["unstaged.txt", "staged.txt", "both.txt", "old.txt", "line\nbreak"]
        for path in paths:
            (self.root / path).write_text("before\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.root, check=True)

        (self.root / "unstaged.txt").write_text("unstaged\n", encoding="utf-8")
        (self.root / "staged.txt").write_text("staged\n", encoding="utf-8")
        subprocess.run(["git", "add", "staged.txt"], cwd=self.root, check=True)
        (self.root / "both.txt").write_text("staged both\n", encoding="utf-8")
        subprocess.run(["git", "add", "both.txt"], cwd=self.root, check=True)
        (self.root / "both.txt").write_text("unstaged both\n", encoding="utf-8")
        subprocess.run(["git", "mv", "old.txt", "renamed.txt"], cwd=self.root, check=True)
        (self.root / "line\nbreak").write_text("newline path\n", encoding="utf-8")

        status = proofrun.core._git_status(self.root)
        self.assertIsNotNone(status)
        changed_paths = status.tracked_paths
        expected: dict[str, str] = {}
        for relative in changed_paths:
            digest = hashlib.sha256(os.fsencode(relative))
            for args in (
                ("diff", "--binary", "--", relative),
                ("diff", "--cached", "--binary", "--", relative),
            ):
                result = proofrun.core._git(self.root, *args, check=False)
                if result.returncode == 0:
                    digest.update(result.stdout)
            expected[relative] = digest.hexdigest()

        with patch("proofrun.core._git", wraps=proofrun.core._git) as git:
            actual = git_state(self.root)

        self.assertEqual(actual.tracked_changes, expected)
        self.assertEqual(git.call_count, 5)

        with patch("proofrun.core._split_diff_blocks", return_value=[]):
            fallback = git_state(self.root)
        self.assertEqual(fallback.tracked_changes, expected)

    def test_passing_check_that_mutates_repository_is_rejected(self) -> None:
        tracked = self.root / "tracked.py"
        tracked.write_text("before\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.py"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.root, check=True)
        store = self.root / ".proofrun" / "receipts.jsonl"
        command = [
            sys.executable,
            "-c",
            "from pathlib import Path; Path('tracked.py').write_text('after\\n'); Path('generated.txt').write_text('new\\n')",
        ]

        exit_code, receipt = run_check(
            name="mutator", command=command, cwd=self.root, store=store
        )
        assessed = assess_receipts(
            [receipt], current=git_state(self.root), max_age_hours=24
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(receipt["command_exit_code"], 0)
        self.assertEqual(receipt["exit_code"], 1)
        self.assertEqual(receipt["schema_version"], 5)
        self.assertTrue(receipt["repository_mutation"]["detected"])
        self.assertFalse(receipt["repository_mutation"]["head_changed"])
        self.assertEqual(
            receipt["repository_mutation"]["tracked_paths"], ["tracked.py"]
        )
        self.assertEqual(
            receipt["repository_mutation"]["untracked_paths"], ["generated.txt"]
        )
        self.assertEqual(assessed[0]["state"], "stale")
        self.assertEqual(
            assessed[0]["reasons"], ["repository changed during check"]
        )
        output = io.StringIO()
        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(output):
                self.assertEqual(main(["--store", str(store), "status"]), 0)
        self.assertIn(
            "repository changed during check: tracked.py, generated.txt",
            output.getvalue(),
        )
        report = render_markdown_report(
            [receipt], current=git_state(self.root), max_age_hours=24
        )
        self.assertIn(
            "- Result: rejected (repository changed; command exit 0)", report
        )
        self.assertIn("- Mutated tracked paths: `tracked.py`", report)
        self.assertIn("- Mutated untracked paths: `generated.txt`", report)

    def test_failing_mutating_check_preserves_command_exit_code(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        exit_code, receipt = run_check(
            name="failing-mutator",
            command=[
                sys.executable,
                "-c",
                "from pathlib import Path; import sys; Path('artifact.txt').write_text('x'); sys.exit(7)",
            ],
            cwd=self.root,
            store=store,
        )

        self.assertEqual(exit_code, 7)
        self.assertEqual(receipt["command_exit_code"], 7)
        self.assertEqual(receipt["exit_code"], 7)
        assessed = assess_receipts(
            [receipt], current=git_state(self.root), max_age_hours=24
        )
        self.assertEqual(
            assessed[0]["reasons"], ["failed", "repository changed during check"]
        )

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

    def test_path_limit_compacts_human_output_but_json_keeps_all_paths(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        run_check(
            name="smoke",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )
        for index in range(12):
            (self.root / f"change-{index:02}.txt").write_text(
                f"{index}\n", encoding="utf-8"
            )

        output = io.StringIO()
        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(output):
                exit_code = main(
                    ["--store", str(store), "status", "--path-limit", "3"]
                )

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "working tree changed: change-00.txt, change-01.txt, change-02.txt, +9 more",
            output.getvalue(),
        )

        output = io.StringIO()
        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(output):
                main(
                    [
                        "--store",
                        str(store),
                        "status",
                        "--path-limit",
                        "1",
                        "--json",
                    ]
                )
        status = json.loads(output.getvalue())
        self.assertEqual(len(status[0]["working_tree_paths"]["untracked"]), 12)

        report = render_markdown_report(
            load_receipts(store),
            current=git_state(self.root),
            max_age_hours=24,
            path_limit=2,
        )
        self.assertIn(
            "- Invalidating untracked paths: `change-00.txt`, `change-01.txt`",
            report,
        )
        self.assertIn("- Additional invalidating paths: 10 not shown", report)

    def test_status_require_valid_accepts_selected_fresh_proof(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        run_check(
            name="unit",
            command=[sys.executable, "-c", "pass"],
            cwd=self.root,
            store=store,
        )
        run_check(
            name="lint",
            command=[sys.executable, "-c", "import sys; sys.exit(3)"],
            cwd=self.root,
            store=store,
        )
        output = io.StringIO()

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(output):
                exit_code = main(
                    ["--store", str(store), "status", "--require-valid", "unit"]
                )

        self.assertEqual(exit_code, 0)
        self.assertIn("VALID  unit: evidence applies", output.getvalue())
        self.assertNotIn("lint", output.getvalue())

    def test_status_require_valid_reports_stale_and_missing_proof_as_json(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        run_check(
            name="lint",
            command=[sys.executable, "-c", "import sys; sys.exit(3)"],
            cwd=self.root,
            store=store,
        )
        output = io.StringIO()

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(output):
                exit_code = main(
                    [
                        "--store",
                        str(store),
                        "status",
                        "--require-valid",
                        "--json",
                        "lint",
                        "integration",
                    ]
                )

        status = json.loads(output.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual([item["name"] for item in status], ["lint", "integration"])
        self.assertEqual([item["state"] for item in status], ["stale", "missing"])
        self.assertEqual(status[1]["reasons"], ["no receipt"])
        self.assertIsNone(status[1]["age_hours"])
        self.assertIsNone(status[1]["receipt"])

    def test_status_require_valid_fails_when_store_is_empty(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        output = io.StringIO()

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(output):
                exit_code = main(
                    ["--store", str(store), "status", "--require-valid"]
                )

        self.assertEqual(exit_code, 1)
        self.assertEqual(output.getvalue(), "No verification receipts yet.\n")

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

        self.assertEqual(first["schema_version"], 5)
        self.assertIsNone(first["previous_hash"])
        self.assertEqual(first["receipt_hash"], receipt_digest(first))
        self.assertEqual(second["previous_hash"], receipt_digest(first))
        self.assertEqual(second["receipt_hash"], receipt_digest(second))
        self.assertEqual(
            [item["state"] for item in audit_receipts([first, second])],
            ["valid", "valid"],
        )

    def test_concurrent_receipt_writers_preserve_one_valid_chain(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        writer_count = 8
        ready = threading.Barrier(writer_count)
        original_digest = receipt_digest

        def slow_digest(receipt: dict[str, object]) -> str:
            time.sleep(0.01)
            return original_digest(receipt)

        def write_receipt(index: int) -> None:
            receipt = {
                "id": f"concurrent-{index}",
                "name": f"check-{index}",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "exit_code": 0,
                "git": {},
            }
            ready.wait()
            append_receipt(store, receipt)

        with patch("proofrun.core.receipt_digest", side_effect=slow_digest):
            with ThreadPoolExecutor(max_workers=writer_count) as executor:
                list(executor.map(write_receipt, range(writer_count)))

        receipts = load_receipts(store)
        self.assertEqual(len(receipts), writer_count)
        self.assertEqual(
            [item["state"] for item in audit_receipts(receipts)],
            ["valid"] * writer_count,
        )

    def test_receipt_reader_waits_for_in_progress_append(self) -> None:
        store = self.root / ".proofrun" / "receipts.jsonl"
        digest_started = threading.Event()
        allow_append = threading.Event()
        original_digest = receipt_digest
        receipt = {
            "id": "blocked-writer",
            "name": "smoke",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "exit_code": 0,
            "git": {},
        }

        def blocking_digest(value: dict[str, object]) -> str:
            digest_started.set()
            allow_append.wait(timeout=2)
            return original_digest(value)

        with patch("proofrun.core.receipt_digest", side_effect=blocking_digest):
            with ThreadPoolExecutor(max_workers=2) as executor:
                writer = executor.submit(append_receipt, store, receipt)
                self.assertTrue(digest_started.wait(timeout=2))
                reader = executor.submit(load_receipts, store)
                time.sleep(0.02)
                self.assertFalse(reader.done())
                allow_append.set()
                writer.result(timeout=2)
                self.assertEqual(reader.result(timeout=2), [receipt])

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
        self.assertIn("receipt chain invalid", report)

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

    def test_init_detects_unittest_and_refuses_to_overwrite_manifest(self) -> None:
        tests = self.root / "tests"
        tests.mkdir()
        (tests / "test_example.py").write_text("", encoding="utf-8")
        output = io.StringIO()

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(output):
                self.assertEqual(main(["init"]), 0)

        manifest = self.root / "proofrun.toml"
        launcher = (
            "python3" if Path(sys.executable).name.startswith("python3") else "python"
        )
        expected = (
            "[checks.test]\n"
            f'command = ["{launcher}", "-B", "-m", "unittest", '
            '"discover", "-s", "tests", "-v"]\n'
        )
        self.assertEqual(manifest.read_text(encoding="utf-8"), expected)
        self.assertIn("detected Python (unittest)", output.getvalue())

        error = io.StringIO()
        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stderr(error):
                self.assertEqual(main(["init", "--", "python", "-m", "pytest"]), 2)
        self.assertIn(
            "refusing to overwrite existing files: proofrun.toml",
            error.getvalue(),
        )
        self.assertEqual(manifest.read_text(encoding="utf-8"), expected)

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(["init", "--force", "--", "python", "-m", "pytest"]),
                    0,
                )
        self.assertEqual(
            manifest.read_text(encoding="utf-8"),
            '[checks.test]\ncommand = ["python", "-m", "pytest"]\n',
        )

    def test_init_detects_supported_projects_and_rejects_ambiguity(self) -> None:
        launcher = (
            "python3" if Path(sys.executable).name.startswith("python3") else "python"
        )
        cases = [
            (
                "pytest",
                (("tests/conftest.py", ""),),
                (launcher, "-B", "-m", "pytest", "-p", "no:cacheprovider"),
            ),
            (
                "node",
                (("package.json", '{"scripts":{"test":"node --test"}}'),),
                ("npm", "test"),
            ),
            ("rust", (("Cargo.toml", ""),), ("cargo", "test")),
            ("go", (("go.mod", ""),), ("go", "test", "./...")),
        ]
        for name, files, expected in cases:
            with self.subTest(name=name):
                root = self.root / name
                for relative, content in files:
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")
                self.assertEqual(detect_project_preset(root).command, expected)

        rust_preset = detect_project_preset(self.root / "rust")
        self.assertEqual(
            rust_preset.env,
            (("CARGO_TARGET_DIR", ".proofrun/cargo-target"),),
        )

        mixed = self.root / "mixed"
        mixed.mkdir()
        (mixed / "package.json").write_text(
            '{"scripts":{"test":"node --test"}}\n', encoding="utf-8"
        )
        (mixed / "go.mod").write_text("module example.test/mixed\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "multiple project types detected"):
            detect_project_preset(mixed)

    def test_init_python_launcher_matches_running_interpreter_family(self) -> None:
        tests = self.root / "tests"
        tests.mkdir()

        cases = [
            ("/usr/local/bin/python3.14", "python3"),
            ("/opt/pypy3/bin/pypy3", "python3"),
            (r"C:\\Python312\\python.exe", "python"),
            ("/workspace/.venv/bin/python", "python"),
        ]
        for executable, expected in cases:
            with self.subTest(executable=executable):
                with patch("proofrun.scaffold.sys.executable", executable):
                    preset = detect_project_preset(self.root)
                self.assertEqual(preset.command[0], expected)

    def test_init_python_unittest_scaffold_verifies_without_mutation(self) -> None:
        tests = self.root / "tests"
        tests.mkdir()
        (tests / "test_smoke.py").write_text(
            "import unittest\n\n"
            "class SmokeTest(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n",
            encoding="utf-8",
        )

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["init"]), 0)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "python fixture"], cwd=self.root, check=True
        )

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["verify"]), 0)

        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(status.stdout, "")

    def test_init_pytest_scaffold_verifies_without_mutation(self) -> None:
        if importlib.util.find_spec("pytest") is None:
            self.skipTest("real pytest runtime is not installed")

        tests = self.root / "tests"
        tests.mkdir()
        (tests / "test_smoke.py").write_text(
            "def test_ok():\n"
            "    assert 6 * 7 == 42\n",
            encoding="utf-8",
        )
        (self.root / "pyproject.toml").write_text(
            "[tool.pytest.ini_options]\naddopts = [\"-q\"]\n",
            encoding="utf-8",
        )
        (self.root / "requirements-test.txt").write_text(
            "pytest>=8\n", encoding="utf-8"
        )

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "init",
                            "--github-actions",
                            "--ci-install",
                            "proofrun @ git+https://example.test/proofrun.git@v1.8.0",
                        ]
                    ),
                    0,
                )

        workflow = (
            self.root / ".github" / "workflows" / "proofrun.yml"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "python -m pip install -r requirements-test.txt pytest", workflow
        )
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "pytest fixture"], cwd=self.root, check=True
        )

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["verify"]), 0)
                self.assertEqual(main(["status", "--require-valid", "test"]), 0)

        self.assertFalse((self.root / ".pytest_cache").exists())
        self.assertFalse(any(self.root.rglob("__pycache__")))
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(status.stdout, "")

    def test_init_rust_scaffold_redirects_build_output_without_mutation(self) -> None:
        (self.root / "Cargo.toml").write_text(
            '[package]\nname = "proofrun-fixture"\nversion = "0.1.0"\n',
            encoding="utf-8",
        )
        source = self.root / "src"
        source.mkdir()
        (source / "lib.rs").write_text(
            "pub fn answer() -> u8 { 42 }\n", encoding="utf-8"
        )

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["init"]), 0)

        manifest = self.root / "proofrun.toml"
        self.assertEqual(
            manifest.read_text(encoding="utf-8"),
            '[checks.test]\ncommand = ["cargo", "test"]\n\n'
            '[checks.test.env]\n'
            'CARGO_TARGET_DIR = ".proofrun/cargo-target"\n',
        )
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "rust fixture"], cwd=self.root, check=True
        )

        with tempfile.TemporaryDirectory() as bin_directory:
            fake_cargo = Path(bin_directory) / "cargo"
            fake_cargo.write_text(
                f"#!{sys.executable}\n"
                "import os, pathlib, sys\n"
                "assert sys.argv[1:] == ['test']\n"
                "target = pathlib.Path(os.environ['CARGO_TARGET_DIR'])\n"
                "target.mkdir(parents=True, exist_ok=True)\n"
                "(target / 'fixture-artifact').write_text('built\\n')\n",
                encoding="utf-8",
            )
            fake_cargo.chmod(0o755)
            path = f"{bin_directory}{os.pathsep}{os.environ.get('PATH', '')}"
            with patch.dict(os.environ, {"PATH": path}):
                with patch("proofrun.cli.Path.cwd", return_value=self.root):
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        self.assertEqual(main(["verify"]), 0)
                        self.assertEqual(
                            main(["status", "--require-valid", "test"]), 0
                        )

        self.assertTrue(
            (self.root / ".proofrun" / "cargo-target" / "fixture-artifact").is_file()
        )
        receipt = load_receipts(self.root / ".proofrun" / "receipts.jsonl")[-1]
        self.assertEqual(
            receipt["context"]["env"],
            {"CARGO_TARGET_DIR": ".proofrun/cargo-target"},
        )
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(status.stdout, "")

    def test_init_uses_declared_or_locked_node_package_manager(self) -> None:
        cases = [
            (
                "declared-pnpm",
                {"packageManager": " pnpm@10.0.0 "},
                None,
                ("pnpm", "test"),
            ),
            ("yarn-lock", {}, "yarn.lock", ("yarn", "test")),
            ("bun-lock", {}, "bun.lock", ("bun", "run", "test")),
        ]
        for name, package_fields, lockfile, expected in cases:
            with self.subTest(name=name):
                root = self.root / name
                root.mkdir()
                package = {"scripts": {"test": "vitest run"}, **package_fields}
                (root / "package.json").write_text(
                    json.dumps(package), encoding="utf-8"
                )
                if lockfile:
                    (root / lockfile).write_text("", encoding="utf-8")
                preset = detect_project_preset(root)
                self.assertEqual(preset.command, expected)
                self.assertIn(expected[0], preset.label)
                if name == "declared-pnpm":
                    self.assertEqual(preset.package_manager_version, "10.0.0")

    def test_init_rejects_unrunnable_or_ambiguous_node_projects(self) -> None:
        cases = [
            ("missing", {}),
            (
                "placeholder",
                {"scripts": {"test": 'echo "Error: no test specified" && exit 1'}},
            ),
            (
                "unversioned-manager",
                {
                    "scripts": {"test": "node --test"},
                    "packageManager": "pnpm",
                },
            ),
        ]
        for name, package in cases:
            with self.subTest(name=name):
                root = self.root / name
                root.mkdir()
                (root / "package.json").write_text(
                    json.dumps(package), encoding="utf-8"
                )
                error = (
                    "manager@version"
                    if name == "unversioned-manager"
                    else "provide a command after --"
                )
                with self.assertRaisesRegex(ValueError, error):
                    detect_project_preset(root)

        ambiguous = self.root / "ambiguous-locks"
        ambiguous.mkdir()
        (ambiguous / "package.json").write_text(
            '{"scripts":{"test":"vitest run"}}', encoding="utf-8"
        )
        (ambiguous / "pnpm-lock.yaml").write_text("", encoding="utf-8")
        (ambiguous / "yarn.lock").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "multiple Node package managers"):
            detect_project_preset(ambiguous)

    def test_init_preflights_all_targets_before_writing(self) -> None:
        workflow = self.root / ".github" / "workflows" / "proofrun.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("existing\n", encoding="utf-8")
        error = io.StringIO()

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stderr(error):
                exit_code = main(
                    [
                        "init",
                        "--github-actions",
                        "--ci-install",
                        "proofrun @ git+https://example.test/proofrun.git@v1.2.0",
                        "--",
                        "python",
                        "-m",
                        "pytest",
                    ]
                )

        self.assertEqual(exit_code, 2)
        self.assertFalse((self.root / "proofrun.toml").exists())
        self.assertEqual(workflow.read_text(encoding="utf-8"), "existing\n")
        self.assertIn(".github/workflows/proofrun.yml", error.getvalue())

    def test_init_creates_custom_manifest_and_runnable_workflow(self) -> None:
        output = io.StringIO()
        requirement = "proofrun @ git+https://example.test/proofrun.git@v1.2.0"

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(output):
                exit_code = main(
                    [
                        "init",
                        "--check-name",
                        "quality",
                        "--github-actions",
                        "--ci-install",
                        requirement,
                        "--",
                        "python",
                        "-m",
                        "pytest",
                        "-q",
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            (self.root / "proofrun.toml").read_text(encoding="utf-8"),
            '[checks.quality]\ncommand = ["python", "-m", "pytest", "-q"]\n',
        )
        workflow = (self.root / ".github" / "workflows" / "proofrun.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("python -m pip install 'proofrun @ git+", workflow)
        self.assertIn("proofrun verify --json", workflow)
        self.assertIn("proofrun status --require-valid", workflow)
        self.assertIn("wrote proofrun.toml", output.getvalue())
        self.assertIn("wrote .github/workflows/proofrun.yml", output.getvalue())

    def test_init_generated_workflow_bootstraps_detected_node_manager(self) -> None:
        cases = [
            (
                "npm",
                {},
                "package-lock.json",
                ("actions/setup-node@v6", "npm ci"),
                ("pnpm/action-setup", "setup-bun", "corepack enable"),
            ),
            (
                "pnpm-declared",
                {"packageManager": "pnpm@10.0.0"},
                None,
                (
                    "actions/setup-node@v6",
                    "pnpm/action-setup@v6",
                    'version: "10.0.0"',
                    "pnpm install",
                ),
                ("version: latest", "setup-bun", "corepack enable"),
            ),
            (
                "pnpm-locked",
                {},
                "pnpm-lock.yaml",
                (
                    "pnpm/action-setup@v6",
                    "version: latest",
                    "pnpm install --frozen-lockfile",
                ),
                ("setup-bun", "corepack enable"),
            ),
            (
                "yarn",
                {},
                "yarn.lock",
                (
                    "actions/setup-node@v6",
                    "corepack enable",
                    "yarn install --frozen-lockfile",
                ),
                ("pnpm/action-setup", "setup-bun"),
            ),
            (
                "bun",
                {},
                "bun.lock",
                ("oven-sh/setup-bun@v2", "bun ci"),
                ("actions/setup-node", "pnpm/action-setup", "corepack enable"),
            ),
        ]
        for name, package_fields, lockfile, expected, absent in cases:
            with self.subTest(name=name):
                root = self.root / name
                root.mkdir()
                package = {"scripts": {"test": "vitest run"}, **package_fields}
                (root / "package.json").write_text(
                    json.dumps(package), encoding="utf-8"
                )
                if lockfile:
                    (root / lockfile).write_text("", encoding="utf-8")

                plan = plan_repository_initialization(
                    root,
                    check_name="test",
                    command=None,
                    github_actions=True,
                    ci_install=(
                        "proofrun @ "
                        "git+https://example.test/proofrun.git@v1.5.0"
                    ),
                    force=False,
                )
                workflow = plan.targets[1].content

                for marker in expected:
                    self.assertIn(marker, workflow)
                for marker in absent:
                    self.assertNotIn(marker, workflow)

    def test_init_generated_workflow_bootstraps_python_test_dependencies(self) -> None:
        cases = [
            (
                "pytest-minimal",
                ("tests/conftest.py",),
                "python -m pip install pytest",
            ),
            (
                "pytest-requirements",
                (
                    "tests/conftest.py",
                    "requirements.txt",
                    "requirements-dev.txt",
                    "requirements-test.txt",
                ),
                (
                    "python -m pip install -r requirements.txt "
                    "-r requirements-dev.txt -r requirements-test.txt pytest"
                ),
            ),
            (
                "unittest-requirements",
                ("tests/test_smoke.py", "requirements.txt"),
                "python -m pip install -r requirements.txt",
            ),
        ]
        for name, files, expected in cases:
            with self.subTest(name=name):
                root = self.root / name
                for relative in files:
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("", encoding="utf-8")

                plan = plan_repository_initialization(
                    root,
                    check_name="test",
                    command=None,
                    github_actions=True,
                    ci_install=(
                        "proofrun @ git+https://example.test/proofrun.git@v1.8.0"
                    ),
                    force=False,
                )
                workflow = plan.targets[1].content

                self.assertIn(expected, workflow)

    def test_init_requires_explicit_ci_install_source(self) -> None:
        error = io.StringIO()
        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stderr(error):
                exit_code = main(
                    ["init", "--github-actions", "--", "python", "-m", "pytest"]
                )

        self.assertEqual(exit_code, 2)
        self.assertFalse((self.root / "proofrun.toml").exists())
        self.assertIn("--github-actions requires --ci-install", error.getvalue())

    def test_init_dry_run_previews_detected_scaffold_without_writing(self) -> None:
        tests = self.root / "tests"
        tests.mkdir()
        output = io.StringIO()

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(output):
                exit_code = main(["init", "--dry-run"])

        self.assertEqual(exit_code, 0)
        self.assertFalse((self.root / "proofrun.toml").exists())
        preview = output.getvalue()
        self.assertIn("detected Python (unittest)", preview)
        self.assertIn("would create proofrun.toml", preview)

    def test_init_json_preview_exposes_declared_package_manager_version(self) -> None:
        (self.root / "package.json").write_text(
            json.dumps(
                {
                    "packageManager": "pnpm@10.28.1+sha512.fixture",
                    "scripts": {"test": "node --test"},
                }
            ),
            encoding="utf-8",
        )
        output = io.StringIO()

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(output):
                self.assertEqual(main(["init", "--dry-run", "--json"]), 0)

        preview = json.loads(output.getvalue())
        self.assertEqual(preview["check"]["package_manager"], "pnpm")
        self.assertEqual(preview["check"]["package_manager_version"], "10.28.1")
        self.assertFalse((self.root / "proofrun.toml").exists())

    def test_init_json_preview_includes_exact_targets_without_writing(self) -> None:
        output = io.StringIO()
        requirement = "proofrun @ git+https://example.test/proofrun.git@v1.4.0"
        manifest = self.root / "proofrun.toml"
        manifest.write_text("existing\n", encoding="utf-8")

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stdout(output):
                exit_code = main(
                    [
                        "init",
                        "--dry-run",
                        "--json",
                        "--force",
                        "--check-name",
                        "quality",
                        "--github-actions",
                        "--ci-install",
                        requirement,
                        "--",
                        "python",
                        "-m",
                        "pytest",
                        "-q",
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertEqual(manifest.read_text(encoding="utf-8"), "existing\n")
        self.assertFalse((self.root / ".github").exists())
        preview = json.loads(output.getvalue())
        self.assertEqual(preview["schema_version"], 1)
        self.assertEqual(preview["mode"], "dry-run")
        self.assertTrue(preview["force"])
        self.assertEqual(preview["check"]["source"], "explicit")
        self.assertIsNone(preview["check"]["package_manager"])
        self.assertEqual(
            preview["check"]["command"], ["python", "-m", "pytest", "-q"]
        )
        self.assertEqual(
            [target["path"] for target in preview["targets"]],
            ["proofrun.toml", ".github/workflows/proofrun.yml"],
        )
        self.assertEqual(
            [target["action"] for target in preview["targets"]],
            ["overwrite", "create"],
        )
        self.assertEqual(
            preview["targets"][0]["content"],
            '[checks.quality]\ncommand = ["python", "-m", "pytest", "-q"]\n',
        )
        self.assertIn(requirement, preview["targets"][1]["content"])

    def test_init_json_requires_dry_run(self) -> None:
        error = io.StringIO()

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with redirect_stderr(error):
                exit_code = main(["init", "--json", "--", "python", "-m", "pytest"])

        self.assertEqual(exit_code, 2)
        self.assertFalse((self.root / "proofrun.toml").exists())
        self.assertIn("--json requires --dry-run", error.getvalue())

    def test_scaffold_apply_rejects_target_that_appeared_after_plan(self) -> None:
        plan = plan_repository_initialization(
            self.root,
            check_name="test",
            command=["python", "-m", "pytest"],
            github_actions=True,
            ci_install="proofrun @ git+https://example.test/proofrun.git@v1.4.0",
            force=False,
        )
        workflow = self.root / ".github" / "workflows" / "proofrun.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("appeared\n", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "changed after planning"):
            apply_scaffold_plan(plan)

        self.assertFalse((self.root / "proofrun.toml").exists())
        self.assertEqual(workflow.read_text(encoding="utf-8"), "appeared\n")

    def test_manifest_context_runs_from_subdirectory_and_is_recorded(self) -> None:
        package = self.root / "packages" / "api"
        package.mkdir(parents=True)
        manifest = self.root / "proofrun.toml"
        manifest.write_text(
            f"""
[checks.context]
command = ["{sys.executable}", "-c", "import os, pathlib; assert pathlib.Path.cwd().name == 'api'; assert os.environ['APP_MODE'] == 'test'"]
cwd = "packages/api"

[checks.context.env]
APP_MODE = "test"
Z_FLAG = "last"
""".strip()
            + "\n",
            encoding="utf-8",
        )
        store = self.root / ".proofrun" / "receipts.jsonl"

        exit_code, results = run_suite(
            load_manifest(manifest), cwd=self.root, store=store
        )

        self.assertEqual(exit_code, 0)
        receipt = results[0]["receipt"]
        self.assertEqual(receipt["context"]["cwd"], "packages/api")
        self.assertEqual(
            receipt["context"]["env"],
            {"APP_MODE": "test", "Z_FLAG": "last"},
        )
        self.assertEqual(receipt["git"]["untracked_files"].keys(), {"proofrun.toml"})
        report = render_markdown_report(
            [receipt], current=git_state(self.root), max_age_hours=24
        )
        self.assertIn("- Working directory: `packages/api`", report)
        self.assertIn("- Environment: `APP_MODE=test`, `Z_FLAG=last`", report)

    def test_manifest_context_is_strictly_validated(self) -> None:
        manifest = self.root / "proofrun.toml"
        invalid_manifests = [
            ('cwd = "../outside"', "cwd must stay within"),
            ('env = ["not", "a", "table"]', "env"),
            ('extra = true', "unsupported key"),
        ]
        for config, message in invalid_manifests:
            with self.subTest(config=config):
                manifest.write_text(
                    f'[checks.unit]\ncommand = ["python3", "-V"]\n{config}\n',
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, message):
                    load_manifest(manifest)

    def test_python_310_fallback_parses_cwd_and_environment_table(self) -> None:
        manifest = self.root / "proofrun.toml"
        manifest.write_text(
            """
[checks.unit]
command = ["python3", "-V"]
cwd = "pkg"

[checks.unit.env]
PYTHONPATH = "../src"
""".strip()
            + "\n",
            encoding="utf-8",
        )

        with patch("proofrun.manifest.tomllib", None):
            check = load_manifest(manifest)[0]

        self.assertEqual(check.cwd, "pkg")
        self.assertEqual(check.env, (("PYTHONPATH", "../src"),))

    def test_suite_rejects_missing_context_directory_before_running(self) -> None:
        manifest = self.root / "proofrun.toml"
        manifest.write_text(
            f"""
[checks.first]
command = ["{sys.executable}", "-c", "print('should not run')"]

[checks.missing]
command = ["{sys.executable}", "-c", "pass"]
cwd = "missing"
""".strip()
            + "\n",
            encoding="utf-8",
        )
        store = self.root / ".proofrun" / "receipts.jsonl"

        with self.assertRaisesRegex(ValueError, "cwd is not a directory"):
            run_suite(load_manifest(manifest), cwd=self.root, store=store)

        self.assertFalse(store.exists())

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

    def test_run_suite_bounds_parallel_jobs_and_preserves_manifest_order(self) -> None:
        checks = [
            CheckDefinition(name=f"check-{index}", command=("unused",))
            for index in range(5)
        ]
        active = 0
        maximum_active = 0
        lock = threading.Lock()
        two_started = threading.Event()
        release = threading.Event()

        def controlled_run_check(**kwargs: object) -> tuple[int, dict[str, object]]:
            nonlocal active, maximum_active
            name = str(kwargs["name"])
            with lock:
                active += 1
                maximum_active = max(maximum_active, active)
                if active == 2:
                    two_started.set()
            release.wait(timeout=2)
            with lock:
                active -= 1
            return 0, {"id": f"receipt-{name}"}

        with patch("proofrun.core.run_check", side_effect=controlled_run_check):
            with ThreadPoolExecutor(max_workers=1) as executor:
                suite = executor.submit(
                    run_suite,
                    checks,
                    cwd=self.root,
                    store=self.root / ".proofrun" / "receipts.jsonl",
                    jobs=2,
                )
                self.assertTrue(two_started.wait(timeout=2))
                self.assertEqual(maximum_active, 2)
                release.set()
                exit_code, results = suite.result(timeout=2)

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            [item["name"] for item in results],
            [check.name for check in checks],
        )
        self.assertLessEqual(maximum_active, 2)

    def test_parallel_fail_fast_finishes_running_checks_without_starting_more(self) -> None:
        checks = [
            CheckDefinition(name=name, command=("unused",))
            for name in ("fail", "in-flight", "later")
        ]
        started: list[str] = []
        lock = threading.Lock()
        two_started = threading.Event()
        failure_observed = threading.Event()
        release_in_flight = threading.Event()

        def controlled_run_check(**kwargs: object) -> tuple[int, dict[str, object]]:
            name = str(kwargs["name"])
            with lock:
                started.append(name)
                if len(started) == 2:
                    two_started.set()
            self.assertTrue(two_started.wait(timeout=2))
            if name == "fail":
                return 9, {"id": "receipt-fail"}
            release_in_flight.wait(timeout=2)
            return 0, {"id": f"receipt-{name}"}

        def observed_wait(*args: object, **kwargs: object) -> object:
            done, pending = wait_for_futures(*args, **kwargs)
            if any(future.result()["exit_code"] != 0 for future in done):
                failure_observed.set()
            return done, pending

        with patch("proofrun.core.run_check", side_effect=controlled_run_check):
            with patch("proofrun.core.wait", side_effect=observed_wait):
                with ThreadPoolExecutor(max_workers=1) as executor:
                    suite = executor.submit(
                        run_suite,
                        checks,
                        cwd=self.root,
                        store=self.root / ".proofrun" / "receipts.jsonl",
                        fail_fast=True,
                        jobs=2,
                    )
                    self.assertTrue(failure_observed.wait(timeout=2))
                    release_in_flight.set()
                    exit_code, results = suite.result(timeout=2)

        self.assertEqual(exit_code, 9)
        self.assertEqual(set(started), {"fail", "in-flight"})
        self.assertEqual([item["name"] for item in results], ["fail", "in-flight"])

    def test_run_suite_rejects_nonpositive_job_count_before_execution(self) -> None:
        check = CheckDefinition(name="unit", command=("unused",))

        with self.assertRaisesRegex(ValueError, "jobs must be one or greater"):
            run_suite(
                [check],
                cwd=self.root,
                store=self.root / ".proofrun" / "receipts.jsonl",
                jobs=0,
            )

    def test_verify_cli_passes_parallel_job_count_to_suite(self) -> None:
        manifest = self.root / "proofrun.toml"
        manifest.write_text(
            '[checks.unit]\ncommand = ["python3", "-V"]\n',
            encoding="utf-8",
        )
        store = self.root / ".proofrun" / "receipts.jsonl"

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with patch("proofrun.cli.run_suite", return_value=(0, [])) as run:
                with redirect_stdout(io.StringIO()):
                    exit_code = main(
                        [
                            "--store",
                            str(store),
                            "verify",
                            "--manifest",
                            str(manifest),
                            "--jobs",
                            "3",
                        ]
                    )

        self.assertEqual(exit_code, 0)
        self.assertEqual(run.call_args.kwargs["jobs"], 3)

    def test_verify_json_is_clean_when_check_writes_to_stdout(self) -> None:
        manifest = self.root / "proofrun.toml"
        manifest.write_text(
            f"""
[checks.noisy]
command = ["{sys.executable}", "-c", "print('check output')"]
""".strip()
            + "\n",
            encoding="utf-8",
        )
        store = self.root / ".proofrun" / "receipts.jsonl"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")

        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "proofrun",
                "--store",
                str(store),
                "verify",
                "--manifest",
                str(manifest),
                "--json",
            ],
            cwd=self.root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        summary = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertIn("check output", completed.stderr)
        self.assertEqual(summary["schema_version"], 1)
        self.assertEqual(summary["state"], "passed")
        self.assertEqual(summary["selected_count"], 1)
        self.assertEqual(summary["executed_count"], 1)
        self.assertEqual(summary["passed_count"], 1)
        self.assertEqual(summary["failed_count"], 0)
        self.assertEqual(summary["skipped_count"], 0)
        self.assertEqual(summary["skipped_checks"], [])
        self.assertEqual(summary["results"][0]["name"], "noisy")
        self.assertEqual(summary["results"][0]["state"], "passed")
        self.assertEqual(summary["results"][0]["exit_code"], 0)
        self.assertIn("receipt_hash", summary["results"][0]["receipt"])

    def test_verify_json_reports_fail_fast_skips_and_exit_code(self) -> None:
        manifest = self.root / "proofrun.toml"
        manifest.write_text(
            """
[checks.fail]
command = ["python3", "-c", "pass"]

[checks.later]
command = ["python3", "-c", "pass"]
""".strip()
            + "\n",
            encoding="utf-8",
        )
        store = self.root / ".proofrun" / "receipts.jsonl"
        results = [
            {
                "name": "fail",
                "command": ["python3", "-c", "pass"],
                "exit_code": 5,
                "receipt": {"id": "failed-receipt", "duration_ms": 12},
            }
        ]
        output = io.StringIO()

        with patch("proofrun.cli.Path.cwd", return_value=self.root):
            with patch("proofrun.cli.run_suite", return_value=(5, results)) as run:
                with redirect_stdout(output):
                    exit_code = main(
                        [
                            "--store",
                            str(store),
                            "verify",
                            "--manifest",
                            str(manifest),
                            "--fail-fast",
                            "--json",
                        ]
                    )

        summary = json.loads(output.getvalue())
        self.assertEqual(exit_code, 5)
        self.assertIs(run.call_args.kwargs["command_stdout"], sys.stderr)
        self.assertEqual(summary["state"], "failed")
        self.assertEqual(summary["exit_code"], 5)
        self.assertEqual(summary["executed_count"], 1)
        self.assertEqual(summary["failed_count"], 1)
        self.assertEqual(summary["skipped_count"], 1)
        self.assertEqual(summary["skipped_checks"], ["later"])
        self.assertEqual(summary["results"][0]["state"], "failed")

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

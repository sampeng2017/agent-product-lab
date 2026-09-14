from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import wheelcontract.core
from wheelcontract.cli import main
from wheelcontract.core import ContractError, load_contract, run_contract


class WheelContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.wheel = self.root / "fixture_cli-1.0.0-py3-none-any.whl"
        with zipfile.ZipFile(self.wheel, "w") as archive:
            archive.writestr("fixture_cli/__init__.py", "")
            archive.writestr(
                "fixture_cli/__main__.py",
                "import json, sys\n"
                "if '--large' in sys.argv:\n    print('x' * 200)\n"
                "elif '--error' in sys.argv:\n"
                "    print('fixture warning', file=sys.stderr)\n"
                "    raise SystemExit(4)\n"
                "elif '--json' in sys.argv:\n"
                "    print(json.dumps({'schema': 3, 'ready': True}))\n"
                "    raise SystemExit(3)\n"
                "else:\n    print('installed hello')\n",
            )
            archive.writestr(
                "fixture_cli-1.0.0.dist-info/METADATA",
                "Metadata-Version: 2.1\nName: fixture-cli\nVersion: 1.0.0\n",
            )
            archive.writestr(
                "fixture_cli-1.0.0.dist-info/WHEEL",
                "Wheel-Version: 1.0\nGenerator: wheelcontract-tests\n"
                "Root-Is-Purelib: true\nTag: py3-none-any\n",
            )
            archive.writestr("fixture_cli-1.0.0.dist-info/RECORD", "")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_contract(self, cases: str, *, limit: int = 65536) -> Path:
        manifest = self.root / "wheelcontract.toml"
        manifest.write_text(
            "schema_version = 1\n"
            "[artifact]\n"
            f"source = {str(self.wheel)!r}\n"
            "[run]\n"
            "timeout_seconds = 10\n"
            f"max_output_bytes = {limit}\n"
            f"{cases}",
            encoding="utf-8",
        )
        return manifest

    def test_installs_wheel_and_checks_all_contract_surfaces(self) -> None:
        manifest = self.write_contract(
            """
[[case]]
name = "human"
argv = ["python", "-m", "fixture_cli"]
stdout_contains = ["installed hello"]

[[case]]
name = "policy-json"
argv = ["python", "-m", "fixture_cli", "--json"]
exit = 3
[case.json]
schema = 3
ready = true

[[case]]
name = "stderr"
argv = ["python", "-m", "fixture_cli", "--error"]
exit = 4
stderr_contains = ["fixture warning"]
"""
        )

        results = run_contract(load_contract(manifest))

        self.assertEqual(
            [result.name for result in results], ["human", "policy-json", "stderr"]
        )
        self.assertTrue(all(result.passed for result in results))

    def test_reports_every_failure_and_returns_one(self) -> None:
        manifest = self.write_contract(
            """
[[case]]
name = "wrong-exit"
argv = ["python", "-m", "fixture_cli", "--json"]
exit = 0

[[case]]
name = "missing-text"
argv = ["python", "-m", "fixture_cli"]
stdout_contains = ["not present"]

[[case]]
name = "wrong-json-field"
argv = ["python", "-m", "fixture_cli", "--json"]
exit = 3
[case.json]
ready = false
"""
        )
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main([str(manifest)])

        self.assertEqual(exit_code, 1)
        self.assertIn("FAIL wrong-exit", output.getvalue())
        self.assertIn("exit was 3; expected 0", output.getvalue())
        self.assertIn("FAIL missing-text", output.getvalue())
        self.assertIn("stdout missing 'not present'", output.getvalue())
        self.assertIn("FAIL wrong-json-field", output.getvalue())
        self.assertIn("JSON field 'ready' was True; expected False", output.getvalue())
        self.assertIn("Result: 0 passed, 3 failed, 3 total", output.getvalue())

    def test_enforces_output_limit(self) -> None:
        manifest = self.write_contract(
            """
[[case]]
name = "large"
argv = ["python", "-m", "fixture_cli", "--large"]
""",
            limit=32,
        )

        result = run_contract(load_contract(manifest))[0]

        self.assertFalse(result.passed)
        self.assertIn("stdout was 201 bytes; limit is 32", result.errors)
        self.assertEqual(len(result.stdout.encode()), 32)

    def test_rejects_unknown_fields_and_unsafe_command_paths(self) -> None:
        manifest = self.write_contract(
            """
[[case]]
name = "unsafe"
argv = ["../fixture", "--version"]
unexpected = "value"
"""
        )

        with self.assertRaisesRegex(ContractError, "unsupported keys"):
            load_contract(manifest)
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace('unexpected = "value"\n', ""),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ContractError, "installed entry point"):
            load_contract(manifest)

    def test_python_310_fallback_parses_supported_contract(self) -> None:
        manifest = self.write_contract(
            """
[[case]]
name = "json"
argv = ["python", "-m", "fixture_cli", "--json"]
exit = 3
stderr_contains = ["warning"]
[case.json]
schema = 3
ready = true
"""
        )

        with patch.object(wheelcontract.core, "tomllib", None):
            contract = load_contract(manifest)

        self.assertEqual(
            contract.cases[0].json_fields, (("schema", 3), ("ready", True))
        )
        self.assertEqual(contract.cases[0].stderr_contains, ("warning",))

    def test_distinguishes_missing_command_from_setup_failure(self) -> None:
        manifest = self.write_contract(
            """
[[case]]
name = "missing-command"
argv = ["does-not-exist"]
"""
        )
        output = io.StringIO()
        error = io.StringIO()

        with redirect_stdout(output), redirect_stderr(error):
            exit_code = main([str(manifest)])

        self.assertEqual(exit_code, 1)
        self.assertIn("installed command not found", output.getvalue())
        self.assertEqual(error.getvalue(), "")

        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                str(self.wheel), str(self.root / "missing.whl")
            ),
            encoding="utf-8",
        )
        output = io.StringIO()
        error = io.StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            exit_code = main([str(manifest)])
        self.assertEqual(exit_code, 2)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("artifact source not found", error.getvalue())

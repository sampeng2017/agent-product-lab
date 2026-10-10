from __future__ import annotations

import io
import json
import os
import tempfile
import time
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

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
                "import json, pathlib, subprocess, sys, time\n"
                "if '--large' in sys.argv:\n    print('x' * 200)\n"
                "elif '--spawn-child' in sys.argv:\n"
                "    marker = sys.argv[sys.argv.index('--spawn-child') + 1]\n"
                "    child = subprocess.Popen([sys.executable, '-c', "
                "'import pathlib, signal, sys, time; '"
                "'signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(2); '"
                "'pathlib.Path(sys.argv[1]).write_text(\"survived\")', "
                "marker])\n"
                "    time.sleep(60)\n"
                "elif '--error' in sys.argv:\n"
                "    print('fixture warning', file=sys.stderr)\n"
                "    raise SystemExit(4)\n"
                "elif '--json-deep' in sys.argv:\n"
                "    print('{\"ready\": true, \"data\": ' + '[' * 5000 + '0' + ']' * 5000 + '}')\n"
                "elif '--json-token' in sys.argv:\n"
                "    print('{\"ready\": true, \"unasserted\": ' + sys.argv[-1] + '}')\n"
                "elif '--json-types' in sys.argv:\n"
                "    print(json.dumps({'one': 1, 'zero': 0, 'truth': True, 'falsehood': False, 'decimal_one': 1.0}))\n"
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

    def test_json_decoder_nesting_limit_fails_case_and_continues_suite(self) -> None:
        manifest = self.write_contract('''
[[case]]
name = "deep-output"
argv = ["python", "-m", "fixture_cli", "--json-deep"]
[case.json]
ready = true

[[case]]
name = "normal-output"
argv = ["python", "-m", "fixture_cli", "--json-token", "0"]
[case.json]
ready = true
''')
        # Decoder depth capacity varies by interpreter and platform. Reproduce
        # its documented error deterministically; normal output is parsed normally.
        decoder = json.loads
        def limited_decoder(value, **options):
            if len(value) > 5000:
                raise RecursionError("fixture decoder depth limit")
            return decoder(value, **options)
        with patch("wheelcontract.core.json.loads", side_effect=limited_decoder):
            results = run_contract(load_contract(manifest))
        self.assertEqual([result.passed for result in results], [False, True])
        self.assertEqual(results[0].errors, ("stdout JSON exceeds decoder nesting limit",))
        self.assertEqual(results[0].exit_code, 0)
        output = io.StringIO()
        with redirect_stdout(output), patch("wheelcontract.core.json.loads", side_effect=limited_decoder):
            self.assertEqual(main([str(manifest)]), 1)
        self.assertIn("PASS normal-output", output.getvalue())
        self.assertIn("Result: 1 passed, 1 failed, 2 total", output.getvalue())

    @unittest.skipUnless(os.name == "posix", "Unix interpreter-launch fixture")
    def test_broken_installed_script_fails_case_and_continues_suite(self) -> None:
        # An installed file is not necessarily runnable. Preserve this raw
        # script's missing interpreter instead of using pip's rewritten #!python.
        with zipfile.ZipFile(self.wheel, "a") as archive:
            script = zipfile.ZipInfo(
                "fixture_cli-1.0.0.data/scripts/fixture-broken"
            )
            script.external_attr = 0o100755 << 16
            archive.writestr(script, "#!/wheelcontract-missing-interpreter\n")
        manifest = self.write_contract('''
[[case]]
name = "broken-launch"
argv = ["fixture-broken"]

[[case]]
name = "normal-launch"
argv = ["python", "-m", "fixture_cli"]
stdout_contains = ["installed hello"]
''')
        results = run_contract(load_contract(manifest))
        self.assertEqual([result.passed for result in results], [False, True])
        self.assertIsNone(results[0].exit_code)
        self.assertEqual(results[0].stdout, "")
        self.assertEqual(results[0].stderr, "")
        self.assertIn("could not start installed command 'fixture-broken'", results[0].errors[0])
        self.assertNotIn(str(self.root), results[0].errors[0])
        output = io.StringIO()
        error = io.StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            self.assertEqual(main([str(manifest)]), 1)
        self.assertEqual(error.getvalue(), "")
        self.assertIn("PASS normal-launch", output.getvalue())
        self.assertIn("Result: 1 passed, 1 failed, 2 total", output.getvalue())

    def test_launch_os_error_diagnostic_is_bounded(self) -> None:
        manifest = self.write_contract('''
[[case]]
name = "denied-launch"
argv = ["python"]
''')
        contract = load_contract(manifest)
        with patch("wheelcontract.core.subprocess.Popen", side_effect=PermissionError(
            13, "denied " * 1000, "/private/temporary-command"
        )):
            result = wheelcontract.core._run_case(
                contract.cases[0], contract, self.root, self.root, self.root, 1
            )
        self.assertFalse(result.passed)
        self.assertIsNone(result.exit_code)
        self.assertIn("OS error 13", result.errors[0])
        self.assertLess(len(result.errors[0]), 320)
        self.assertNotIn("/private/temporary-command", result.errors[0])

    def test_nonstandard_json_constants_fail_even_in_unasserted_nested_values(self) -> None:
        tokens = ('NaN', 'Infinity', '-Infinity', '[NaN]', '{"value": Infinity}', '"NaN"', '{"text": "Infinity"}')
        manifest = self.write_contract("".join(
            f'[[case]]\nname = "token-{index}"\n'
            f'argv = ["python", "-m", "fixture_cli", "--json-token", {json.dumps(token)}]\n'
            '[case.json]\nready = true\n\n'
            for index, token in enumerate(tokens)
        ))
        results = run_contract(load_contract(manifest))
        self.assertEqual([result.passed for result in results], [False] * 5 + [True, True])
        for result in results[:5]:
            self.assertIn("stdout is not JSON: nonstandard constant", result.errors[0])
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main([str(manifest)]), 1)
        self.assertIn("Result: 2 passed, 5 failed, 7 total", output.getvalue())

    def test_json_booleans_cannot_satisfy_numeric_expectations_or_reverse(self) -> None:
        cases = (
            ("numbers-as-booleans", "one = true\nzero = false\n"),
            ("booleans-as-numbers", "truth = 1\nfalsehood = 0\n"),
            ("booleans-match", "truth = true\nfalsehood = false\n"),
            ("numbers-match", "one = 1\nzero = 0\ndecimal_one = 1\n"),
            ("strings-do-not-coerce", 'one = "1"\n'),
        )
        manifest = self.write_contract("".join(
            f'[[case]]\nname = "{name}"\n'
            'argv = ["python", "-m", "fixture_cli", "--json-types"]\n'
            f"[case.json]\n{expectations}\n"
            for name, expectations in cases
        ))
        results = run_contract(load_contract(manifest))
        self.assertEqual([result.passed for result in results], [False, False, True, True, False])
        self.assertEqual(len(results[0].errors), 2)
        self.assertEqual(len(results[1].errors), 2)
        self.assertIn("JSON field 'one' was 1; expected True", results[0].errors)
        self.assertIn("JSON field 'truth' was True; expected 1", results[1].errors)
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main([str(manifest)]), 1)
        self.assertIn("Result: 2 passed, 3 failed, 5 total", output.getvalue())

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

    def test_timeout_terminates_spawned_children(self) -> None:
        marker = self.root / "child-survived"
        manifest = self.write_contract(
            f"""
[[case]]
name = "spawn-timeout"
argv = ["python", "-m", "fixture_cli", "--spawn-child", {str(marker)!r}]
"""
        )
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                "timeout_seconds = 10", "timeout_seconds = 1"
            ),
            encoding="utf-8",
        )

        result = run_contract(load_contract(manifest))[0]
        time.sleep(1.5)

        self.assertFalse(result.passed)
        self.assertIn("timed out after 1s", result.errors)
        self.assertFalse(marker.exists(), "timed-out descendant survived")

    def test_windows_timeout_uses_native_tree_termination(self) -> None:
        process = Mock(pid=1234)
        process.wait.return_value = 1

        with (
            patch.object(wheelcontract.core.os, "name", "nt"),
            patch.object(wheelcontract.core.subprocess, "run") as run,
        ):
            wheelcontract.core._terminate_process_tree(process)

        run.assert_called_once_with(
            ["taskkill", "/PID", "1234", "/T", "/F"],
            stdout=wheelcontract.core.subprocess.DEVNULL,
            stderr=wheelcontract.core.subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
        process.wait.assert_called_once_with(timeout=0.5)

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

    def test_python_310_fallback_rejects_duplicate_keys_and_sections(self) -> None:
        manifest = self.write_contract(
            """
[[case]]
name = "json"
name = "duplicate"
argv = ["python", "-m", "fixture_cli"]
"""
        )

        with (
            patch.object(wheelcontract.core, "tomllib", None),
            self.assertRaisesRegex(ContractError, "duplicate key 'name'"),
        ):
            load_contract(manifest)

        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                'name = "duplicate"\n', "[case.json]\n[case.json]\n"
            ),
            encoding="utf-8",
        )
        with (
            patch.object(wheelcontract.core, "tomllib", None),
            self.assertRaisesRegex(ContractError, "duplicate section \\[case.json\\]"),
        ):
            load_contract(manifest)

    def test_wheel_override_requires_an_existing_wheel_file(self) -> None:
        manifest = self.write_contract(
            """
[[case]]
name = "human"
argv = ["python", "-m", "fixture_cli"]
"""
        )

        for override in (self.root, self.root / "missing.whl", manifest):
            with self.subTest(override=override):
                output = io.StringIO()
                error = io.StringIO()
                with redirect_stdout(output), redirect_stderr(error):
                    exit_code = main(["--wheel", str(override), str(manifest)])
                self.assertEqual(exit_code, 2)
                self.assertEqual(output.getvalue(), "")
                self.assertIn(
                    "--wheel must name an existing .whl file", error.getvalue()
                )

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

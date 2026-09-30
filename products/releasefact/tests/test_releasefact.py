from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import releasefact.core
from releasefact.cli import main
from releasefact.core import ContractError, check_contract, load_contract


class ReleaseFactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_project(self, version: str = "1.2.3") -> Path:
        (self.root / "pyproject.toml").write_text(
            f'[project]\nname = "example"\nversion = "{version}"\n',
            encoding="utf-8",
        )
        (self.root / "package.py").write_text(
            f'__version__ = "{version}"\n', encoding="utf-8"
        )
        (self.root / "README.md").write_text(
            f"Example v{version} is current.\n", encoding="utf-8"
        )
        manifest = self.root / "releasefact.toml"
        manifest.write_text(
            'schema_version = 1\n'
            '[canonical]\nfile = "pyproject.toml"\nkey = "project.version"\n'
            '[[claim]]\nname = "package"\nfile = "package.py"\n'
            'template = "__version__ = \\"{version}\\""\n'
            '[[claim]]\nname = "documentation"\nfile = "README.md"\n'
            'template = "Example v{version} is current."\n',
            encoding="utf-8",
        )
        return manifest

    def test_matching_claims_pass_in_declaration_order(self) -> None:
        manifest = self.write_project()

        canonical, results = check_contract(load_contract(manifest))

        self.assertEqual(canonical, "1.2.3")
        self.assertEqual(
            [result.name for result in results], ["package", "documentation"]
        )
        self.assertTrue(all(result.matched for result in results))
        self.assertEqual([result.line for result in results], [1, 1])

    def test_stale_fixture_reports_every_actual_version_and_returns_one(self) -> None:
        fixture = (
            Path(__file__).parent
            / "fixtures"
            / "stale-release"
            / "releasefact.toml"
        )
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main([str(fixture)])

        self.assertEqual(exit_code, 1)
        self.assertIn(
            "DRIFT package: src/fixture/__init__.py:1 is '0.2.0'; "
            "expected '1.0.0'",
            output.getvalue(),
        )
        self.assertIn(
            "DRIFT installed contract: contract.toml:1 is '0.3.0'; "
            "expected '1.0.0'",
            output.getvalue(),
        )
        self.assertIn(
            "DRIFT portfolio documentation: README.md:1 is '0.1.0'; "
            "expected '1.0.0'",
            output.getvalue(),
        )
        self.assertIn("0 matched, 3 drifted, 3 total", output.getvalue())

    def test_invalid_selector_is_setup_error_and_returns_two(self) -> None:
        manifest = self.write_project()
        (self.root / "README.md").write_text(
            "Example v1.2.3 is current.\nExample v1.2.2 is current.\n",
            encoding="utf-8",
        )
        output = io.StringIO()
        error = io.StringIO()

        with redirect_stdout(output), redirect_stderr(error):
            exit_code = main([str(manifest)])

        self.assertEqual(exit_code, 2)
        self.assertEqual(output.getvalue(), "")
        self.assertIn(
            "template matched multiple lines in README.md: 1, 2", error.getvalue()
        )

    def test_rejects_unknown_fields_unsafe_paths_and_vague_templates(self) -> None:
        manifest = self.write_project()
        text = manifest.read_text(encoding="utf-8")
        manifest.write_text(
            text.replace(
                'name = "package"', 'name = "package"\nextra = "unsupported"'
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ContractError, "unsupported keys"):
            load_contract(manifest)

        manifest.write_text(
            text.replace('file = "package.py"', 'file = "../outside.py"'),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ContractError, "escapes the contract directory"):
            load_contract(manifest)

        manifest.write_text(
            text.replace('__version__ = \\"{version}\\"', "{version}"),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ContractError, "must include literal context"):
            load_contract(manifest)

    def test_python_310_fallback_reads_manifest_and_canonical_value(self) -> None:
        manifest = self.write_project()

        with patch.object(releasefact.core, "tomllib", None):
            contract = load_contract(manifest)
            canonical, results = check_contract(contract)

        self.assertEqual(canonical, "1.2.3")
        self.assertTrue(all(result.matched for result in results))


if __name__ == "__main__":
    unittest.main()

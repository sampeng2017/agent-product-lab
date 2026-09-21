from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import wheelfact.core
from wheelfact.cli import main
from wheelfact.core import ContractError, check_wheel, load_contract


class WheelFactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_contract(
        self,
        *,
        distribution: str = "example-cli",
        version: str = "1.2.3",
        requires_python: str = ">=3.10",
        license_name: str = "MIT",
        scripts: tuple[tuple[str, str], ...] = (("example", "example.cli:main"),),
        members: tuple[str, ...] = ("example/__init__.py", "example/cli.py"),
    ) -> Path:
        script_lines = "\n".join(f'{name} = "{target}"' for name, target in scripts)
        member_lines = "\n".join(f'  "{member}",' for member in members)
        path = self.root / "wheelfact.toml"
        path.write_text(
            "schema_version = 1\n\n"
            "[wheel]\n"
            f'distribution = "{distribution}"\n'
            f'version = "{version}"\n'
            f'requires_python = "{requires_python}"\n'
            f'license = "{license_name}"\n'
            f"package_members = [\n{member_lines}\n]\n\n"
            "[wheel.console_scripts]\n"
            f"{script_lines}\n",
            encoding="utf-8",
        )
        return path

    def write_wheel(
        self,
        *,
        distribution: str = "example-cli",
        version: str = "1.2.3",
        requires_python: str = ">=3.10",
        license_name: str = "MIT",
        scripts: tuple[tuple[str, str], ...] = (("example", "example.cli:main"),),
        members: tuple[str, ...] = ("example/__init__.py", "example/cli.py"),
    ) -> Path:
        wheel = self.root / "example-1.2.3-py3-none-any.whl"
        dist_info = "example_cli-1.2.3.dist-info"
        metadata = (
            "Metadata-Version: 2.2\n"
            f"Name: {distribution}\n"
            f"Version: {version}\n"
            f"Requires-Python: {requires_python}\n"
            f"License: {license_name}\n\n"
        )
        entry_points = "[console_scripts]\n" + "\n".join(
            f"{name} = {target}" for name, target in scripts
        )
        with ZipFile(wheel, "w") as archive:
            for member in members:
                archive.writestr(member, "")
            archive.writestr(f"{dist_info}/METADATA", metadata)
            archive.writestr(f"{dist_info}/entry_points.txt", entry_points)
            archive.writestr(f"{dist_info}/WHEEL", "Wheel-Version: 1.0\n")
            archive.writestr(f"{dist_info}/RECORD", "")
        return wheel

    def run_cli(self, contract: Path, wheel: Path) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main([str(contract), str(wheel)])
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_exact_contract_passes_with_deterministic_facts(self) -> None:
        contract = self.write_contract()
        wheel = self.write_wheel()

        exit_code, stdout, stderr = self.run_cli(contract, wheel)

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("PASS distribution: 'example-cli'", stdout)
        self.assertIn("PASS console script example: 'example.cli:main'", stdout)
        self.assertIn("PASS member example/cli.py: 'example/cli.py'", stdout)
        self.assertIn("Result: 7 matched, 0 mismatched, 7 total", stdout)

    def test_reports_all_scalar_script_and_member_mismatches(self) -> None:
        contract = self.write_contract(
            distribution="expected-cli",
            version="9.0.0",
            requires_python=">=3.11",
            license_name="Apache-2.0",
            scripts=(("expected", "expected.cli:main"),),
            members=("expected/__init__.py",),
        )
        wheel = self.write_wheel(
            scripts=(("actual", "example.cli:main"),),
            members=("example/__init__.py",),
        )

        exit_code, stdout, stderr = self.run_cli(contract, wheel)

        self.assertEqual(exit_code, 1)
        self.assertEqual(stderr, "")
        self.assertIn("MISMATCH distribution: was 'example-cli'; expected 'expected-cli'", stdout)
        self.assertIn("MISMATCH version: was '1.2.3'; expected '9.0.0'", stdout)
        self.assertIn("UNEXPECTED console script actual: 'example.cli:main'", stdout)
        self.assertIn("MISSING console script expected: expected 'expected.cli:main'", stdout)
        self.assertIn("UNEXPECTED member example/__init__.py", stdout)
        self.assertIn("MISSING member expected/__init__.py", stdout)
        self.assertIn("Result: 0 matched, 8 mismatched, 8 total", stdout)

    def test_invalid_or_ambiguous_wheel_is_setup_error(self) -> None:
        contract = self.write_contract()
        unsafe = self.write_wheel(members=("../escape.py",))
        exit_code, stdout, stderr = self.run_cli(contract, unsafe)
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("unsafe wheel member", stderr)

        ambiguous = self.root / "ambiguous.whl"
        with ZipFile(ambiguous, "w") as archive:
            archive.writestr("one.dist-info/METADATA", "Name: one\nVersion: 1\n\n")
            archive.writestr("two.dist-info/METADATA", "Name: two\nVersion: 2\n\n")
        with self.assertRaisesRegex(ContractError, "exactly one .dist-info"):
            check_wheel(ambiguous, load_contract(contract))

    def test_contract_is_strict_and_rejects_unsafe_or_duplicate_members(self) -> None:
        contract = self.write_contract()
        original = contract.read_text(encoding="utf-8")
        contract.write_text(
            original.replace('[wheel]\n', '[wheel]\nextra = true\n'),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ContractError, "unsupported keys: extra"):
            load_contract(contract)

        contract.write_text(
            original.replace('  "example/cli.py",', '  "../outside.py",'),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ContractError, "unsafe contract package member"):
            load_contract(contract)

        contract.write_text(
            original.replace('  "example/cli.py",', '  "example/__init__.py",'),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ContractError, "duplicate package member"):
            load_contract(contract)

        contract.write_text(
            original.replace('  "example/cli.py",', '  "example//cli.py",'),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ContractError, "unsafe contract package member"):
            load_contract(contract)

    def test_python_310_fallback_parses_multiline_contract(self) -> None:
        contract_path = self.write_contract()
        wheel = self.write_wheel()

        with patch.object(wheelfact.core, "tomllib", None):
            contract = load_contract(contract_path)
            results = check_wheel(wheel, contract)

        self.assertTrue(all(result.matched for result in results))


if __name__ == "__main__":
    unittest.main()

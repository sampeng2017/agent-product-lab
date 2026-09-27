from __future__ import annotations

import base64
import csv
import hashlib
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
        modern_license: bool = False,
        scripts: tuple[tuple[str, str], ...] = (("example", "example.cli:main"),),
        members: tuple[str, ...] = ("example/__init__.py", "example/cli.py"),
        record_corruption: str | None = None,
    ) -> Path:
        prefix = record_corruption or "example"
        wheel = self.root / f"{prefix}-1.2.3-py3-none-any.whl"
        dist_info = "example_cli-1.2.3.dist-info"
        metadata_version = "2.4" if modern_license else "2.2"
        license_header = "License-Expression" if modern_license else "License"
        metadata = (
            f"Metadata-Version: {metadata_version}\n"
            f"Name: {distribution}\n"
            f"Version: {version}\n"
            f"Requires-Python: {requires_python}\n"
            f"{license_header}: {license_name}\n\n"
        )
        entry_points = "[console_scripts]\n" + "\n".join(
            f"{name} = {target}" for name, target in scripts
        )
        contents = {member: b"" for member in members}
        contents[f"{dist_info}/METADATA"] = metadata.encode("utf-8")
        contents[f"{dist_info}/entry_points.txt"] = entry_points.encode("utf-8")
        contents[f"{dist_info}/WHEEL"] = b"Wheel-Version: 1.0\n"
        record_rows = []
        for name, content in contents.items():
            digest = base64.urlsafe_b64encode(
                hashlib.sha256(content).digest()
            ).rstrip(b"=")
            record_rows.append(
                [name, f"sha256={digest.decode('ascii')}", str(len(content))]
            )
        if record_corruption in {
            "wrong-digest",
            "wrong-size",
            "missing-row",
            "weak-hash",
            "missing-hash",
            "invalid-size",
            "duplicate-row",
        }:
            payload_row = next(row for row in record_rows if row[0] == "example/cli.py")
            if record_corruption == "wrong-digest":
                payload_row[1] = "sha256=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            elif record_corruption == "wrong-size":
                payload_row[2] = str(int(payload_row[2]) + 1)
            elif record_corruption == "weak-hash":
                digest = base64.urlsafe_b64encode(
                    hashlib.sha1(b"").digest()
                ).rstrip(b"=")
                payload_row[1] = f"sha1={digest.decode('ascii')}"
            elif record_corruption == "missing-hash":
                payload_row[1] = ""
            elif record_corruption == "invalid-size":
                payload_row[2] = "many"
            elif record_corruption == "duplicate-row":
                record_rows.append(payload_row.copy())
            else:
                record_rows.remove(payload_row)
        record_name = f"{dist_info}/RECORD"
        record_rows.append([record_name, "", ""])
        if record_corruption == "absent-file-row":
            record_rows.append(["example/absent.py", "sha256=AAAA", "0"])
        elif record_corruption == "record-self-hash":
            record_rows[-1][1] = "sha256=AAAA"
        record_output = io.StringIO(newline="")
        csv.writer(record_output, lineterminator="\n").writerows(record_rows)
        if record_corruption != "missing-record":
            contents[record_name] = record_output.getvalue().encode("utf-8")
        if record_corruption == "unrecorded-member":
            contents["example/unrecorded.py"] = b"VALUE = True\n"
        with ZipFile(wheel, "w") as archive:
            for name, content in contents.items():
                archive.writestr(name, content)
        return wheel

    def run_cli(self, contract: Path, wheel: Path) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main([str(contract), str(wheel)])
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_exact_contract_passes_with_deterministic_facts(self) -> None:
        contract = self.write_contract()
        wheel = self.write_wheel(modern_license=True)

        exit_code, stdout, stderr = self.run_cli(contract, wheel)

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")
        self.assertIn("PASS distribution: 'example-cli'", stdout)
        self.assertIn("PASS license: 'MIT'", stdout)
        self.assertIn("PASS console script example: 'example.cli:main'", stdout)
        self.assertIn("PASS member example/cli.py: 'example/cli.py'", stdout)
        self.assertIn("Result: 7 matched, 0 mismatched, 7 total", stdout)

    def test_legacy_license_metadata_remains_supported(self) -> None:
        contract = self.write_contract()
        results = check_wheel(self.write_wheel(), load_contract(contract))

        self.assertTrue(all(result.matched for result in results))

    def test_record_integrity_rejects_hash_size_and_membership_corruption(self) -> None:
        contract = self.write_contract()
        expected = {
            "wrong-digest": "hash mismatch for example/cli.py",
            "wrong-size": "size mismatch for example/cli.py",
            "missing-row": "missing rows: example/cli.py",
            "unrecorded-member": "missing rows: example/unrecorded.py",
        }

        for corruption, diagnostic in expected.items():
            with self.subTest(corruption=corruption):
                exit_code, stdout, stderr = self.run_cli(
                    contract, self.write_wheel(record_corruption=corruption)
                )

                self.assertEqual(exit_code, 2)
                self.assertEqual(stdout, "")
                self.assertIn("wheel RECORD is invalid", stderr)
                self.assertIn(diagnostic, stderr)

    def test_record_integrity_rejects_weak_or_malformed_evidence(self) -> None:
        contract = self.write_contract()
        expected = {
            "weak-hash": "weak hash algorithm for example/cli.py: sha1",
            "missing-hash": "missing hash for example/cli.py",
            "invalid-size": "invalid size for example/cli.py: 'many'",
            "duplicate-row": "duplicate row for example/cli.py",
            "absent-file-row": "rows for absent files: example/absent.py",
            "record-self-hash": "RECORD row must have empty hash and size",
        }

        for corruption, diagnostic in expected.items():
            with self.subTest(corruption=corruption):
                exit_code, stdout, stderr = self.run_cli(
                    contract, self.write_wheel(record_corruption=corruption)
                )

                self.assertEqual(exit_code, 2)
                self.assertEqual(stdout, "")
                self.assertIn("wheel RECORD is invalid", stderr)
                self.assertIn(diagnostic, stderr)

        exit_code, stdout, stderr = self.run_cli(
            contract, self.write_wheel(record_corruption="missing-record")
        )
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("wheel RECORD not found", stderr)

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

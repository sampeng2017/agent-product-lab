from __future__ import annotations

import ast
import base64
import configparser
import csv
import hashlib
import io
from dataclasses import dataclass
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import BadZipFile, ZipFile

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised through fallback tests
    tomllib = None


_MAX_ARCHIVE_ENTRIES = 10_000
_MAX_CONTROL_BYTES = 1024 * 1024
_MAX_VERIFIED_BYTES = 1024 * 1024 * 1024
_HASH_CHUNK_BYTES = 64 * 1024


class ContractError(ValueError):
    """The contract or wheel cannot be inspected safely and unambiguously."""


@dataclass(frozen=True)
class Contract:
    distribution: str
    version: str
    requires_python: str
    license: str
    console_scripts: tuple[tuple[str, str], ...]
    package_members: tuple[str, ...]


@dataclass(frozen=True)
class CheckResult:
    label: str
    actual: str | None
    expected: str | None

    @property
    def matched(self) -> bool:
        return self.actual is not None and self.actual == self.expected


def load_contract(path: Path) -> Contract:
    if not path.is_file():
        raise ContractError(f"contract not found: {path}")
    try:
        data = _parse_toml(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ContractError(f"cannot parse {path}: {exc}") from exc
    root = _require_table(data, "contract")
    _reject_unknown(root, {"schema_version", "wheel"}, "contract")
    if root.get("schema_version") != 1:
        raise ContractError("schema_version must be 1")
    wheel = _require_table(root.get("wheel"), "[wheel]")
    _reject_unknown(
        wheel,
        {
            "distribution",
            "version",
            "requires_python",
            "license",
            "console_scripts",
            "package_members",
        },
        "[wheel]",
    )
    console = _require_table(wheel.get("console_scripts"), "[wheel.console_scripts]")
    console_scripts: list[tuple[str, str]] = []
    for name, target in console.items():
        console_scripts.append(
            (
                _required_string(name, "console script name"),
                _required_string(target, f"console script {name!r}"),
            )
        )
    raw_members = wheel.get("package_members")
    if not isinstance(raw_members, list) or not raw_members:
        raise ContractError("[wheel].package_members must be a non-empty string array")
    members: list[str] = []
    for value in raw_members:
        member = _required_string(value, "package member")
        _validate_member(member, "contract package member", allow_directory=False)
        if member in members:
            raise ContractError(f"duplicate package member: {member}")
        members.append(member)
    return Contract(
        distribution=_required_string(wheel.get("distribution"), "[wheel].distribution"),
        version=_required_string(wheel.get("version"), "[wheel].version"),
        requires_python=_required_string(
            wheel.get("requires_python"), "[wheel].requires_python"
        ),
        license=_required_string(wheel.get("license"), "[wheel].license"),
        console_scripts=tuple(sorted(console_scripts)),
        package_members=tuple(sorted(members)),
    )


def check_wheel(path: Path, contract: Contract) -> tuple[CheckResult, ...]:
    _validate_wheel_path(path)
    try:
        with ZipFile(path) as archive:
            file_names, dist_root = _verify_archive(archive)
            metadata_name = f"{dist_root}/METADATA"
            metadata = BytesParser().parsebytes(
                _read_control_file(archive, metadata_name)
            )
            actual_metadata = {
                "distribution": _single_header(metadata, "Name", required=True),
                "version": _single_header(metadata, "Version", required=True),
                "requires-python": _single_header(metadata, "Requires-Python"),
                "license": _metadata_license(metadata),
            }
            entry_name = f"{dist_root}/entry_points.txt"
            actual_scripts = (
                _read_console_scripts(_read_control_file(archive, entry_name), entry_name)
                if entry_name in file_names
                else {}
            )
            actual_members = tuple(
                sorted(
                    name
                    for name in file_names
                    if not name.startswith(f"{dist_root}/")
                )
            )
    except ContractError:
        raise
    except (BadZipFile, OSError, RuntimeError, ValueError) as exc:
        raise ContractError(f"cannot inspect wheel {path}: {exc}") from exc

    results = [
        CheckResult("distribution", actual_metadata["distribution"], contract.distribution),
        CheckResult("version", actual_metadata["version"], contract.version),
        CheckResult(
            "requires-python", actual_metadata["requires-python"], contract.requires_python
        ),
        CheckResult("license", actual_metadata["license"], contract.license),
    ]
    expected_scripts = dict(contract.console_scripts)
    for name in sorted(set(actual_scripts) | set(expected_scripts)):
        results.append(
            CheckResult(
                f"console script {name}", actual_scripts.get(name), expected_scripts.get(name)
            )
        )
    actual_member_set = set(actual_members)
    expected_member_set = set(contract.package_members)
    for name in sorted(actual_member_set | expected_member_set):
        results.append(
            CheckResult(
                f"member {name}",
                name if name in actual_member_set else None,
                name if name in expected_member_set else None,
            )
        )
    return tuple(results)


def verify_wheel_integrity(path: Path) -> None:
    """Reject unsafe wheel structure or internally inconsistent RECORD evidence."""
    _validate_wheel_path(path)
    try:
        with ZipFile(path) as archive:
            _verify_archive(archive)
    except ContractError:
        raise
    except (BadZipFile, OSError, RuntimeError, ValueError) as exc:
        raise ContractError(f"cannot inspect wheel {path}: {exc}") from exc


def _validate_wheel_path(path: Path) -> None:
    if not path.is_file() or path.suffix != ".whl":
        raise ContractError(f"wheel must be an existing .whl file: {path}")


def _verify_archive(archive: ZipFile) -> tuple[list[str], str]:
    names = archive.namelist()
    if len(names) > _MAX_ARCHIVE_ENTRIES:
        raise ContractError(
            f"wheel has {len(names)} entries; limit is {_MAX_ARCHIVE_ENTRIES}"
        )
    if len(names) != len(set(names)):
        duplicates = sorted(name for name in set(names) if names.count(name) > 1)
        raise ContractError(f"wheel has duplicate entries: {', '.join(duplicates)}")
    for name in names:
        _validate_member(name, "wheel member", allow_directory=True)
    file_names = [name for name in names if not name.endswith("/")]
    dist_roots = {
        part
        for name in file_names
        for part in PurePosixPath(name).parts
        if part.endswith(".dist-info")
    }
    if len(dist_roots) != 1:
        raise ContractError(
            f"wheel must contain exactly one .dist-info directory; found {len(dist_roots)}"
        )
    dist_root = next(iter(dist_roots))
    metadata_name = f"{dist_root}/METADATA"
    if metadata_name not in file_names:
        raise ContractError(f"wheel metadata not found: {metadata_name}")
    record_name = f"{dist_root}/RECORD"
    if record_name not in file_names:
        raise ContractError(f"wheel RECORD not found: {record_name}")
    _verify_record(archive, file_names, record_name)
    return file_names, dist_root


def _read_control_file(archive: ZipFile, name: str) -> bytes:
    info = archive.getinfo(name)
    if info.file_size > _MAX_CONTROL_BYTES:
        raise ContractError(
            f"wheel control file {name} is {info.file_size} bytes; "
            f"limit is {_MAX_CONTROL_BYTES}"
        )
    return archive.read(info)


def _verify_record(archive: ZipFile, file_names: list[str], record_name: str) -> None:
    try:
        record_text = _read_control_file(archive, record_name).decode("utf-8")
        rows = list(csv.reader(io.StringIO(record_text, newline=""), strict=True))
    except (csv.Error, UnicodeError) as exc:
        raise ContractError(f"cannot parse wheel RECORD {record_name}: {exc}") from exc

    entries: dict[str, tuple[str, str]] = {}
    issues: list[str] = []
    for row_number, row in enumerate(rows, start=1):
        if len(row) != 3:
            issues.append(f"row {row_number} has {len(row)} fields; expected 3")
            continue
        name, hash_value, size_value = row
        try:
            _validate_member(name, "RECORD path", allow_directory=False)
        except ContractError as exc:
            issues.append(str(exc))
            continue
        if name in entries:
            issues.append(f"duplicate row for {name}")
            continue
        entries[name] = (hash_value, size_value)

    signature_names = {f"{record_name}.jws", f"{record_name}.p7s"}
    expected_names = set(file_names) - signature_names
    actual_names = set(entries)
    missing = sorted(expected_names - actual_names)
    unexpected = sorted(actual_names - expected_names)
    if missing:
        issues.append(f"missing rows: {', '.join(missing)}")
    if unexpected:
        issues.append(f"rows for absent files: {', '.join(unexpected)}")

    if record_name in entries and entries[record_name] != ("", ""):
        issues.append("RECORD row must have empty hash and size")

    verified_bytes = sum(
        archive.getinfo(name).file_size
        for name in expected_names
        if name != record_name
    )
    if verified_bytes > _MAX_VERIFIED_BYTES:
        raise ContractError(
            f"wheel files total {verified_bytes} bytes; "
            f"RECORD verification limit is {_MAX_VERIFIED_BYTES}"
        )

    for name in sorted(expected_names & actual_names - {record_name}):
        hash_value, size_value = entries[name]
        if not hash_value:
            issues.append(f"missing hash for {name}")
            continue
        algorithm, separator, encoded_digest = hash_value.partition("=")
        if not separator or not algorithm or not encoded_digest:
            issues.append(f"invalid hash for {name}: {hash_value!r}")
            continue
        try:
            verifier = hashlib.new(algorithm)
        except ValueError:
            issues.append(f"unsupported hash algorithm for {name}: {algorithm}")
            continue
        normalized_algorithm = algorithm.lower().replace("-", "").replace("_", "")
        if (
            verifier.digest_size < hashlib.sha256().digest_size
            or "md5" in normalized_algorithm
            or "sha1" in normalized_algorithm
        ):
            issues.append(f"weak hash algorithm for {name}: {algorithm}")
            continue
        try:
            expected_digest = _decode_record_digest(encoded_digest)
        except ValueError:
            issues.append(f"invalid {algorithm} digest for {name}")
            continue
        if len(expected_digest) != verifier.digest_size:
            issues.append(f"invalid {algorithm} digest length for {name}")
            continue
        actual_size = 0
        with archive.open(name) as source:
            while True:
                chunk = source.read(_HASH_CHUNK_BYTES)
                if not chunk:
                    break
                actual_size += len(chunk)
                verifier.update(chunk)
        if verifier.digest() != expected_digest:
            issues.append(f"hash mismatch for {name}")
        if size_value:
            if not size_value.isascii() or not size_value.isdecimal():
                issues.append(f"invalid size for {name}: {size_value!r}")
            elif int(size_value) != actual_size:
                issues.append(
                    f"size mismatch for {name}: RECORD has {size_value}; "
                    f"archive has {actual_size}"
                )

    if issues:
        raise ContractError(f"wheel RECORD is invalid: {'; '.join(issues)}")


def _decode_record_digest(value: str) -> bytes:
    if "=" in value:
        raise ValueError("padded digest")
    padding = "=" * (-len(value) % 4)
    return base64.b64decode(
        (value + padding).encode("ascii"), altchars=b"-_", validate=True
    )


def _single_header(message: Any, name: str, *, required: bool = False) -> str | None:
    values = message.get_all(name, [])
    if len(values) > 1:
        raise ContractError(f"wheel METADATA repeats {name}")
    value = values[0].strip() if values else None
    if required and not value:
        raise ContractError(f"wheel METADATA is missing {name}")
    return value or None


def _metadata_license(message: Any) -> str | None:
    expression = _single_header(message, "License-Expression")
    legacy = _single_header(message, "License")
    return expression or legacy


def _read_console_scripts(content: bytes, display_name: str) -> dict[str, str]:
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str
    try:
        parser.read_string(content.decode("utf-8"))
    except (UnicodeError, configparser.Error) as exc:
        raise ContractError(f"cannot parse {display_name}: {exc}") from exc
    if not parser.has_section("console_scripts"):
        return {}
    scripts: dict[str, str] = {}
    for name, target in parser.items("console_scripts"):
        scripts[_required_string(name, "wheel console script name")] = _required_string(
            target, f"wheel console script {name!r}"
        )
    return scripts


def _validate_member(value: str, label: str, *, allow_directory: bool) -> None:
    path = PurePosixPath(value)
    comparable = value[:-1] if value.endswith("/") else value
    if (
        not value
        or "\0" in value
        or value.startswith("/")
        or "\\" in value
        or (value.endswith("/") and not allow_directory)
        or not path.parts
        or path.parts[0].endswith(":")
        or ".." in path.parts
        or any(not part for part in path.parts)
        or path.as_posix() != comparable
    ):
        raise ContractError(f"unsafe {label}: {value!r}")


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\0" in value:
        raise ContractError(f"{label} must be a non-empty string")
    return value


def _require_table(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a table")
    return value


def _reject_unknown(table: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(table) - allowed)
    if unknown:
        raise ContractError(f"{label} has unsupported keys: {', '.join(unknown)}")


def _parse_toml(text: str) -> dict[str, Any]:
    if tomllib is not None:
        return tomllib.loads(text)
    return _parse_toml_fallback(text)


def _parse_toml_fallback(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    wheel: dict[str, Any] = {}
    console: dict[str, Any] = {}
    current = data
    lines = iter(enumerate(text.splitlines(), start=1))
    for line_number, raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[wheel]":
            if "wheel" in data:
                raise ValueError(f"duplicate section [wheel] on line {line_number}")
            data["wheel"] = wheel
            current = wheel
            continue
        if line == "[wheel.console_scripts]":
            if "console_scripts" in wheel:
                raise ValueError(
                    f"duplicate section [wheel.console_scripts] on line {line_number}"
                )
            wheel["console_scripts"] = console
            current = console
            continue
        if line.startswith("["):
            raise ValueError(f"unsupported section on line {line_number}: {line}")
        key, separator, raw_value = line.partition("=")
        key = key.strip().strip('"')
        if not separator or not key:
            raise ValueError(f"invalid assignment on line {line_number}")
        if key in current:
            raise ValueError(f"duplicate key {key!r} on line {line_number}")
        value_text = raw_value.strip()
        if value_text.startswith("[") and not value_text.rstrip().endswith("]"):
            parts = [value_text]
            for continued_number, continued in lines:
                parts.append(continued.strip())
                if continued.strip().endswith("]"):
                    break
            else:
                raise ValueError(f"unterminated array on line {line_number}")
            value_text = "\n".join(parts)
        try:
            current[key] = ast.literal_eval(value_text)
        except (SyntaxError, ValueError) as exc:
            raise ValueError(f"invalid value on line {line_number}") from exc
    return data

from __future__ import annotations

import ast
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .core import CheckDefinition

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    tomllib = None


SECTION_PREFIX = "checks."
SECTION_PATTERN = re.compile(r"^\[checks\.([A-Za-z0-9_-]+)\]$")


def load_manifest(path: Path) -> list[CheckDefinition]:
    if not path.exists():
        raise ValueError(f"manifest not found: {path}")

    data = _parse_manifest(path.read_text(encoding="utf-8"))
    checks = data.get("checks")
    if not isinstance(checks, Mapping) or not checks:
        raise ValueError("manifest must define at least one [checks.<name>] entry")

    definitions: list[CheckDefinition] = []
    for name, config in checks.items():
        if not isinstance(name, str) or not name:
            raise ValueError("check names must be non-empty strings")
        if not isinstance(config, Mapping):
            raise ValueError(f"check {name!r} must be a table")
        command = config.get("command")
        if not isinstance(command, list) or not command or not all(
            isinstance(part, str) and part for part in command
        ):
            raise ValueError(f"check {name!r} must define a non-empty string array command")
        definitions.append(CheckDefinition(name=name, command=tuple(command)))
    return definitions


def select_checks(
    checks: list[CheckDefinition],
    names: list[str] | tuple[str, ...],
) -> list[CheckDefinition]:
    if not names:
        return checks

    by_name = {check.name: check for check in checks}
    selected: list[CheckDefinition] = []
    missing: list[str] = []
    for name in names:
        check = by_name.get(name)
        if check is None:
            missing.append(name)
        else:
            selected.append(check)
    if missing:
        available = ", ".join(sorted(by_name))
        raise ValueError(
            f"unknown checks: {', '.join(missing)}"
            + (f" (available: {available})" if available else "")
        )
    return selected


def _parse_manifest(text: str) -> dict[str, Any]:
    if tomllib is not None:
        return tomllib.loads(text)
    return _parse_manifest_fallback(text)


def _parse_manifest_fallback(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {"checks": {}}
    current: dict[str, Any] | None = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        section_match = SECTION_PATTERN.match(line)
        if section_match:
            name = section_match.group(1)
            current = {}
            data["checks"][name] = current
            continue

        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            if section.startswith(SECTION_PREFIX):
                raise ValueError(f"invalid manifest section on line {line_number}: {line}")
            raise ValueError(
                "fallback parser only supports [checks.<name>] sections on Python 3.10"
            )

        if current is None:
            raise ValueError(f"expected a [checks.<name>] section before line {line_number}")

        key, separator, value = line.partition("=")
        if separator != "=":
            raise ValueError(f"invalid manifest assignment on line {line_number}")
        key = key.strip()
        if key != "command":
            raise ValueError(
                f"unsupported key {key!r} on line {line_number}; only command is allowed"
            )
        try:
            parsed = ast.literal_eval(value.strip())
        except (SyntaxError, ValueError) as exc:
            raise ValueError(f"invalid command array on line {line_number}") from exc
        current[key] = parsed

    return data

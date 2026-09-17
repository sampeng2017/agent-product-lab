from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised through fallback tests
    tomllib = None


_VERSION_SLOT = "{version}"


class ContractError(ValueError):
    """The release-fact declaration or one of its selectors is invalid."""


@dataclass(frozen=True)
class Claim:
    name: str
    path: Path
    display_path: str
    template: str


@dataclass(frozen=True)
class Contract:
    manifest_path: Path
    canonical_path: Path
    canonical_display_path: str
    canonical_key: str
    claims: tuple[Claim, ...]


@dataclass(frozen=True)
class ClaimResult:
    name: str
    path: str
    line: int
    actual: str
    expected: str

    @property
    def matched(self) -> bool:
        return self.actual == self.expected


def load_contract(path: Path) -> Contract:
    manifest_path = path.resolve()
    if not manifest_path.is_file():
        raise ContractError(f"contract not found: {path}")
    try:
        text = manifest_path.read_text(encoding="utf-8")
        data = _parse_manifest(text)
    except (OSError, UnicodeError, ValueError) as exc:
        raise ContractError(f"cannot parse {path}: {exc}") from exc

    _require_table(data, "contract")
    _reject_unknown(data, {"schema_version", "canonical", "claim"}, "contract")
    if data.get("schema_version") != 1:
        raise ContractError("schema_version must be 1")

    root = manifest_path.parent
    canonical = _require_table(data.get("canonical"), "[canonical]")
    _reject_unknown(canonical, {"file", "key"}, "[canonical]")
    canonical_file = _required_string(canonical.get("file"), "[canonical].file")
    canonical_key = _required_string(canonical.get("key"), "[canonical].key")
    if any(not part for part in canonical_key.split(".")):
        raise ContractError("[canonical].key must be a dotted key without empty parts")
    canonical_path, canonical_display = _contained_path(root, canonical_file)

    raw_claims = data.get("claim")
    if not isinstance(raw_claims, list) or not raw_claims:
        raise ContractError("contract must define at least one [[claim]]")
    claims: list[Claim] = []
    names: set[str] = set()
    for index, value in enumerate(raw_claims, start=1):
        label = f"[[claim]] #{index}"
        raw_claim = _require_table(value, label)
        _reject_unknown(raw_claim, {"name", "file", "template"}, label)
        name = _required_string(raw_claim.get("name"), f"{label}.name")
        if name in names:
            raise ContractError(f"duplicate claim name: {name}")
        names.add(name)
        claim_file = _required_string(raw_claim.get("file"), f"{label}.file")
        template = _required_string(raw_claim.get("template"), f"{label}.template")
        if "\n" in template or "\r" in template:
            raise ContractError(f"claim {name!r} template must be one line")
        if template.count(_VERSION_SLOT) != 1:
            raise ContractError(
                f"claim {name!r} template must contain {_VERSION_SLOT!r} exactly once"
            )
        prefix, suffix = template.split(_VERSION_SLOT)
        if not prefix and not suffix:
            raise ContractError(f"claim {name!r} template must include literal context")
        claim_path, claim_display = _contained_path(root, claim_file)
        claims.append(Claim(name, claim_path, claim_display, template))

    return Contract(
        manifest_path=manifest_path,
        canonical_path=canonical_path,
        canonical_display_path=canonical_display,
        canonical_key=canonical_key,
        claims=tuple(claims),
    )


def check_contract(contract: Contract) -> tuple[str, tuple[ClaimResult, ...]]:
    canonical = _read_canonical(
        contract.canonical_path,
        contract.canonical_display_path,
        contract.canonical_key,
    )
    results = tuple(_check_claim(claim, canonical) for claim in contract.claims)
    return canonical, results


def _read_canonical(path: Path, display_path: str, dotted_key: str) -> str:
    if not path.is_file():
        raise ContractError(f"canonical file not found: {display_path}")
    try:
        text = path.read_text(encoding="utf-8")
        if tomllib is None:
            value = _read_toml_string_fallback(text, dotted_key)
        else:
            document: object = tomllib.loads(text)
            for part in dotted_key.split("."):
                if not isinstance(document, dict) or part not in document:
                    raise ContractError(f"canonical key not found: {dotted_key}")
                document = document[part]
            value = document
    except ContractError:
        raise
    except (OSError, UnicodeError, ValueError) as exc:
        raise ContractError(
            f"cannot read canonical TOML {display_path}: {exc}"
        ) from exc
    if not isinstance(value, str) or not value:
        raise ContractError(f"canonical key {dotted_key!r} must be a non-empty string")
    return value


def _check_claim(claim: Claim, canonical: str) -> ClaimResult:
    if not claim.path.is_file():
        raise ContractError(f"claim {claim.name!r} file not found: {claim.display_path}")
    try:
        lines = claim.path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ContractError(
            f"cannot read claim {claim.name!r} file {claim.display_path}: {exc}"
        ) from exc
    prefix, suffix = claim.template.split(_VERSION_SLOT)
    matches: list[tuple[int, str]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.startswith(prefix) or not line.endswith(suffix):
            continue
        end = len(line) - len(suffix) if suffix else len(line)
        if end >= len(prefix):
            matches.append((line_number, line[len(prefix) : end]))
    if not matches:
        raise ContractError(
            f"claim {claim.name!r} template matched no line in {claim.display_path}"
        )
    if len(matches) > 1:
        lines_text = ", ".join(str(line) for line, _ in matches)
        raise ContractError(
            f"claim {claim.name!r} template matched multiple lines in "
            f"{claim.display_path}: {lines_text}"
        )
    line, actual = matches[0]
    return ClaimResult(claim.name, claim.display_path, line, actual, canonical)


def _contained_path(root: Path, value: str) -> tuple[Path, str]:
    raw = Path(value)
    if raw.is_absolute():
        raise ContractError(f"file paths must be relative to the contract: {value}")
    resolved = (root / raw).resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise ContractError(
            f"file path escapes the contract directory: {value}"
        ) from exc
    return resolved, relative.as_posix()


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


def _parse_manifest(text: str) -> dict[str, Any]:
    if tomllib is not None:
        return tomllib.loads(text)
    return _parse_manifest_fallback(text)


def _parse_manifest_fallback(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current = data
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[canonical]":
            if "canonical" in data:
                raise ValueError(f"duplicate section [canonical] on line {line_number}")
            current = {}
            data["canonical"] = current
            continue
        if line == "[[claim]]":
            current = {}
            claims = data.setdefault("claim", [])
            if not isinstance(claims, list):
                raise ValueError(f"duplicate key 'claim' on line {line_number}")
            claims.append(current)
            continue
        if line.startswith("["):
            raise ValueError(f"unsupported section on line {line_number}: {line}")
        key, separator, raw_value = line.partition("=")
        key = key.strip()
        if not separator or not key:
            raise ValueError(f"invalid assignment on line {line_number}")
        if key in current:
            raise ValueError(f"duplicate key {key!r} on line {line_number}")
        try:
            current[key] = ast.literal_eval(raw_value.strip())
        except (SyntaxError, ValueError) as exc:
            raise ValueError(f"invalid value on line {line_number}") from exc
    return data


def _read_toml_string_fallback(text: str, dotted_key: str) -> object:
    wanted_parts = dotted_key.split(".")
    wanted_section = ".".join(wanted_parts[:-1])
    wanted_key = wanted_parts[-1]
    section = ""
    found: object | None = None
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]") and not line.startswith("[["):
            section = line[1:-1].strip()
            continue
        key, separator, raw_value = line.partition("=")
        if section != wanted_section or not separator or key.strip() != wanted_key:
            continue
        if found is not None:
            raise ContractError(f"duplicate canonical key {dotted_key!r}")
        try:
            found = ast.literal_eval(raw_value.strip())
        except (SyntaxError, ValueError) as exc:
            raise ContractError(
                f"canonical key {dotted_key!r} is not a basic quoted string"
            ) from exc
    if found is None:
        raise ContractError(f"canonical key not found: {dotted_key}")
    return found

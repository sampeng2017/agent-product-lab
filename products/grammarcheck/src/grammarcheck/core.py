from __future__ import annotations

import ast
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path, PurePath


class InspectionError(ValueError):
    """The requested source set cannot be inspected safely and completely."""


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    column: int
    message: str


@dataclass(frozen=True)
class CheckResult:
    target: tuple[int, int]
    files: tuple[str, ...]
    total_bytes: int
    findings: tuple[Finding, ...]


def parse_target(value: str) -> tuple[int, int]:
    parts = value.split(".")
    if len(parts) != 2 or parts[0] != "3" or not parts[1].isdigit():
        raise InspectionError("target must use MAJOR.MINOR form for Python 3")
    target = (3, int(parts[1]))
    current = sys.version_info[:2]
    if target < (3, 7):
        raise InspectionError("target must be Python 3.7 or newer")
    if target > current:
        raise InspectionError(
            f"target Python {value} is newer than running Python {current[0]}.{current[1]}"
        )
    return target


def check_sources(
    root: Path,
    requested: list[str],
    target: tuple[int, int],
    *,
    max_files: int = 10_000,
    max_file_bytes: int = 1024 * 1024,
    max_total_bytes: int = 50 * 1024 * 1024,
) -> CheckResult:
    root = root.resolve()
    if not root.is_dir():
        raise InspectionError(f"root must be an existing directory: {root}")
    if not requested:
        raise InspectionError("at least one source file or directory is required")
    for label, value in (
        ("max files", max_files),
        ("max file bytes", max_file_bytes),
        ("max total bytes", max_total_bytes),
    ):
        if value <= 0:
            raise InspectionError(f"{label} must be positive")

    selected: dict[str, Path] = {}
    for raw in requested:
        relative = PurePath(raw)
        if relative.is_absolute() or (not relative.parts and raw != ".") or ".." in relative.parts:
            raise InspectionError(f"source path must be a safe relative path: {raw!r}")
        source = root if raw == "." else root.joinpath(*relative.parts)
        if source.is_symlink():
            raise InspectionError(f"source path cannot be a symlink: {raw}")
        if source.is_file():
            if source.suffix != ".py":
                raise InspectionError(f"source file must end in .py: {raw}")
            candidates = [source]
        elif source.is_dir():
            candidates = sorted(source.rglob("*.py"))
        else:
            raise InspectionError(f"source path not found: {raw}")
        for candidate in candidates:
            if candidate.is_symlink():
                raise InspectionError(
                    f"Python source cannot be a symlink: {candidate.relative_to(root)}"
                )
            resolved = candidate.resolve()
            try:
                label = resolved.relative_to(root).as_posix()
            except ValueError as exc:
                raise InspectionError(f"source escapes root: {candidate}") from exc
            selected[label] = resolved
            if len(selected) > max_files:
                raise InspectionError(
                    f"source set exceeds {max_files} files; narrow paths or raise --max-files"
                )
    if not selected:
        raise InspectionError("source paths contain no .py files")

    findings: list[Finding] = []
    total_bytes = 0
    for label, path in sorted(selected.items()):
        try:
            size = path.stat().st_size
        except OSError as exc:
            raise InspectionError(f"cannot inspect {label}: {exc}") from exc
        if size > max_file_bytes:
            raise InspectionError(
                f"{label} is {size} bytes; per-file limit is {max_file_bytes}"
            )
        total_bytes += size
        if total_bytes > max_total_bytes:
            raise InspectionError(
                f"source set exceeds {max_total_bytes} bytes at {label}"
            )
        try:
            with tokenize.open(path) as source_file:
                source = source_file.read()
            tree = ast.parse(
                source,
                filename=label,
                mode="exec",
                type_comments=True,
                feature_version=target,
            )
            compile(tree, label, "exec", dont_inherit=True)
        except SyntaxError as exc:
            findings.append(
                Finding(
                    path=label,
                    line=exc.lineno or 0,
                    column=exc.offset or 0,
                    message=exc.msg,
                )
            )
        except (LookupError, OSError, UnicodeError, ValueError) as exc:
            raise InspectionError(f"cannot read {label}: {exc}") from exc
    return CheckResult(target, tuple(sorted(selected)), total_bytes, tuple(findings))

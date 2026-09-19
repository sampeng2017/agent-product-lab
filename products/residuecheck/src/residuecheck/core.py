from __future__ import annotations

import hashlib
import os
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence


class SnapshotError(RuntimeError):
    """The requested tree cannot be inspected within its declared bounds."""


@dataclass(frozen=True)
class Limits:
    max_entries: int = 10_000
    max_file_bytes: int = 16 * 1024 * 1024
    max_total_bytes: int = 256 * 1024 * 1024


@dataclass(frozen=True)
class Snapshot:
    fingerprints: dict[str, str]
    entries: int
    bytes_hashed: int


@dataclass(frozen=True)
class Change:
    kind: str
    path: str


@dataclass(frozen=True)
class CheckResult:
    before: Snapshot
    after: Snapshot
    changes: tuple[Change, ...]
    command_exit: int


def normalize_exclusions(values: Sequence[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in values:
        candidate = PurePosixPath(value.replace(os.sep, "/"))
        if value == "" or candidate.is_absolute() or ".." in candidate.parts:
            raise SnapshotError(f"invalid exclusion {value!r}: use a contained relative path")
        text = candidate.as_posix().rstrip("/")
        if text in {"", "."}:
            raise SnapshotError("cannot exclude the entire inspection root")
        if text not in normalized:
            normalized.append(text)
    return tuple(normalized)


def snapshot(root: Path, *, exclusions: Sequence[str], limits: Limits) -> Snapshot:
    root = root.resolve()
    if not root.is_dir():
        raise SnapshotError(f"inspection root is not a directory: {root}")
    _validate_limits(limits)
    excluded = normalize_exclusions(exclusions)
    fingerprints: dict[str, str] = {}
    entries = 0
    bytes_hashed = 0

    def visit(directory: Path, relative_directory: str = "") -> None:
        nonlocal entries, bytes_hashed
        try:
            with os.scandir(directory) as iterator:
                children = sorted(iterator, key=lambda item: item.name)
        except OSError as exc:
            raise SnapshotError(f"cannot scan {_display(relative_directory)}: {exc}") from exc
        for child in children:
            relative = f"{relative_directory}/{child.name}" if relative_directory else child.name
            relative = PurePosixPath(relative).as_posix()
            if _is_excluded(relative, excluded):
                continue
            entries += 1
            if entries > limits.max_entries:
                raise SnapshotError(
                    f"entry limit exceeded after {limits.max_entries} entries at {relative}"
                )
            try:
                metadata = child.stat(follow_symlinks=False)
                mode = stat.S_IMODE(metadata.st_mode)
                if child.is_symlink():
                    target = os.readlink(child.path)
                    fingerprints[relative] = _fingerprint("link", mode, os.fsencode(target))
                elif child.is_dir(follow_symlinks=False):
                    visit(Path(child.path), relative)
                elif child.is_file(follow_symlinks=False):
                    size = metadata.st_size
                    if size > limits.max_file_bytes:
                        raise SnapshotError(
                            f"file size limit exceeded at {relative}: "
                            f"{size} > {limits.max_file_bytes} bytes"
                        )
                    if bytes_hashed + size > limits.max_total_bytes:
                        raise SnapshotError(
                            f"total byte limit exceeded at {relative}: "
                            f"more than {limits.max_total_bytes} bytes"
                        )
                    digest, actual_size = _hash_file(
                        Path(child.path),
                        mode,
                        max_file_bytes=limits.max_file_bytes,
                        max_total_bytes=limits.max_total_bytes - bytes_hashed,
                        display_path=relative,
                    )
                    fingerprints[relative] = digest
                    bytes_hashed += actual_size
                else:
                    raise SnapshotError(f"unsupported filesystem entry: {relative}")
            except SnapshotError:
                raise
            except OSError as exc:
                raise SnapshotError(f"cannot inspect {relative}: {exc}") from exc

    visit(root)
    return Snapshot(fingerprints, entries, bytes_hashed)


def run_check(
    root: Path,
    command: Sequence[str],
    *,
    exclusions: Sequence[str] = (".git",),
    limits: Limits = Limits(),
) -> CheckResult:
    if not command:
        raise SnapshotError("a command is required after --")
    resolved_root = root.resolve()
    before = snapshot(resolved_root, exclusions=exclusions, limits=limits)
    try:
        completed = subprocess.run(list(command), cwd=resolved_root, check=False)
    except OSError as exc:
        raise SnapshotError(f"cannot start command {command[0]!r}: {exc}") from exc
    after = snapshot(resolved_root, exclusions=exclusions, limits=limits)
    return CheckResult(before, after, compare(before, after), completed.returncode)


def compare(before: Snapshot, after: Snapshot) -> tuple[Change, ...]:
    previous = before.fingerprints
    current = after.fingerprints
    changes = [Change("created", path) for path in current.keys() - previous.keys()]
    changes.extend(Change("removed", path) for path in previous.keys() - current.keys())
    changes.extend(
        Change("modified", path)
        for path in previous.keys() & current.keys()
        if previous[path] != current[path]
    )
    order = {"created": 0, "modified": 1, "removed": 2}
    return tuple(sorted(changes, key=lambda item: (item.path, order[item.kind])))


def _hash_file(
    path: Path,
    mode: int,
    *,
    max_file_bytes: int,
    max_total_bytes: int,
    display_path: str,
) -> tuple[str, int]:
    digest = hashlib.sha256()
    digest.update(f"file\0{mode:o}\0".encode())
    bytes_read = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            bytes_read += len(chunk)
            if bytes_read > max_file_bytes:
                raise SnapshotError(
                    f"file size limit exceeded while reading {display_path}: "
                    f"more than {max_file_bytes} bytes"
                )
            if bytes_read > max_total_bytes:
                raise SnapshotError(
                    f"total byte limit exceeded at {display_path}: "
                    "file changed while being inspected"
                )
            digest.update(chunk)
    return digest.hexdigest(), bytes_read


def _fingerprint(kind: str, mode: int, content: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(f"{kind}\0{mode:o}\0".encode())
    digest.update(content)
    return digest.hexdigest()


def _is_excluded(path: str, exclusions: Sequence[str]) -> bool:
    return any(path == excluded or path.startswith(f"{excluded}/") for excluded in exclusions)


def _validate_limits(limits: Limits) -> None:
    for name, value in (
        ("max entries", limits.max_entries),
        ("max file bytes", limits.max_file_bytes),
        ("max total bytes", limits.max_total_bytes),
    ):
        if value < 0:
            raise SnapshotError(f"{name} must be nonnegative")


def _display(path: str) -> str:
    return path or "."

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence


SCHEMA_VERSION = 3
DEFAULT_STORE = Path(".proofrun/receipts.jsonl")


@dataclass(frozen=True)
class GitState:
    available: bool
    head: str | None
    branch: str | None
    dirty: bool
    fingerprint: str | None
    tracked_changes: dict[str, str]
    untracked_files: dict[str, str]


@dataclass(frozen=True)
class CheckDefinition:
    name: str
    command: tuple[str, ...]


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def _untracked_files(cwd: Path) -> list[Path]:
    result = _git(
        cwd,
        "ls-files",
        "--others",
        "--exclude-standard",
        "-z",
        check=False,
    )
    if result.returncode != 0:
        return []
    return [cwd / os.fsdecode(name) for name in result.stdout.split(b"\0") if name]


def _tracked_files(cwd: Path) -> list[str]:
    paths: set[str] = set()
    for args in (("diff", "--name-only", "-z"), ("diff", "--cached", "--name-only", "-z")):
        result = _git(cwd, *args, check=False)
        if result.returncode != 0:
            continue
        for name in result.stdout.split(b"\0"):
            if name:
                paths.add(os.fsdecode(name))
    return sorted(paths)


def _file_digest(path: Path, relative: str) -> str:
    digest = hashlib.sha256()
    digest.update(relative.encode())
    try:
        digest.update(path.read_bytes())
    except (OSError, IsADirectoryError):
        digest.update(b"<unreadable>")
    return digest.hexdigest()


def _tracked_change_digests(cwd: Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for relative in _tracked_files(cwd):
        digest = hashlib.sha256()
        digest.update(relative.encode())
        for args in (
            ("diff", "--binary", "--", relative),
            ("diff", "--cached", "--binary", "--", relative),
        ):
            result = _git(cwd, *args, check=False)
            if result.returncode == 0:
                digest.update(result.stdout)
        digests[relative] = digest.hexdigest()
    return digests


def _untracked_file_digests(cwd: Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for path in sorted(_untracked_files(cwd)):
        relative = path.relative_to(cwd).as_posix()
        digests[relative] = _file_digest(path, relative)
    return digests


def _fingerprint_for_state(
    head: str | None,
    tracked_changes: dict[str, str],
    untracked_files: dict[str, str],
) -> str:
    digest = hashlib.sha256()
    digest.update((head or "unborn").encode())
    for relative, value in sorted(tracked_changes.items()):
        digest.update(relative.encode())
        digest.update(value.encode())
    for relative, value in sorted(untracked_files.items()):
        digest.update(relative.encode())
        digest.update(value.encode())
    return digest.hexdigest()


def git_state(cwd: Path) -> GitState:
    cwd = cwd.resolve()
    probe = _git(cwd, "rev-parse", "--is-inside-work-tree", check=False)
    if probe.returncode != 0 or probe.stdout.strip() != b"true":
        return GitState(False, None, None, False, None, {}, {})

    head_result = _git(cwd, "rev-parse", "HEAD", check=False)
    head = head_result.stdout.decode().strip() if head_result.returncode == 0 else None
    branch_result = _git(cwd, "branch", "--show-current", check=False)
    branch = branch_result.stdout.decode().strip() or None

    tracked_changes = _tracked_change_digests(cwd)
    untracked_files = _untracked_file_digests(cwd)
    status = _git(cwd, "status", "--porcelain", "--untracked-files=all", check=False)
    dirty = bool(status.stdout.strip())
    return GitState(
        True,
        head,
        branch,
        dirty,
        _fingerprint_for_state(head, tracked_changes, untracked_files),
        tracked_changes,
        untracked_files,
    )


def ensure_store(store: Path) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    if store.parent.name == ".proofrun":
        ignore = store.parent / ".gitignore"
        if not ignore.exists():
            # Keep runtime evidence, including this ignore file, out of the
            # repository state that receipts fingerprint.
            ignore.write_text("*\n", encoding="utf-8")


def receipt_digest(receipt: dict[str, Any]) -> str:
    """Return the canonical digest used to seal and link a receipt."""
    payload = dict(receipt)
    payload.pop("receipt_hash", None)
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def append_receipt(store: Path, receipt: dict[str, Any]) -> None:
    ensure_store(store)
    previous = load_receipts(store)
    receipt["schema_version"] = SCHEMA_VERSION
    receipt["previous_hash"] = receipt_digest(previous[-1]) if previous else None
    receipt.pop("receipt_hash", None)
    receipt["receipt_hash"] = receipt_digest(receipt)
    with store.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, sort_keys=True) + "\n")


def load_receipts(store: Path) -> list[dict[str, Any]]:
    if not store.exists():
        return []
    receipts: list[dict[str, Any]] = []
    with store.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                receipts.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid receipt at {store}:{line_number}") from exc
    return receipts


def audit_receipts(receipts: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Check receipt hashes and links while tolerating legacy unsealed entries."""
    receipt_list = list(receipts)
    results: list[dict[str, Any]] = []
    chain_started = False
    chain_broken = False

    for index, receipt in enumerate(receipt_list):
        schema_version = receipt.get("schema_version", 1)
        sealed = (
            (isinstance(schema_version, int) and schema_version >= 3)
            or "receipt_hash" in receipt
            or "previous_hash" in receipt
        )
        issues: list[str] = []

        if not sealed:
            if chain_started:
                issues.append("unsealed receipt after chain start")
                chain_broken = True
                state = "invalid"
            else:
                state = "unsealed"
        else:
            chain_started = True
            expected_hash = receipt_digest(receipt)
            if receipt.get("receipt_hash") != expected_hash:
                issues.append("receipt hash mismatch")

            expected_previous = (
                receipt_digest(receipt_list[index - 1]) if index > 0 else None
            )
            if receipt.get("previous_hash") != expected_previous:
                issues.append("previous receipt link mismatch")

            if chain_broken:
                issues.append("earlier chain failure")
            if issues:
                chain_broken = True
                state = "invalid"
            else:
                state = "valid"

        results.append(
            {
                "index": index + 1,
                "id": receipt.get("id"),
                "name": receipt.get("name", "unnamed"),
                "state": state,
                "issues": issues,
            }
        )
    return results


def run_check(
    *,
    name: str,
    command: Sequence[str],
    cwd: Path,
    store: Path,
) -> tuple[int, dict[str, Any]]:
    if not command:
        raise ValueError("a command is required")

    ensure_store(store)
    started_at = datetime.now(timezone.utc)
    start = time.monotonic()
    try:
        completed = subprocess.run(list(command), cwd=cwd, check=False)
        exit_code = completed.returncode
    except FileNotFoundError:
        exit_code = 127
    duration_ms = round((time.monotonic() - start) * 1000)
    state = git_state(cwd)
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "id": uuid.uuid4().hex[:12],
        "name": name,
        "command": list(command),
        "started_at": started_at.isoformat(),
        "duration_ms": duration_ms,
        "exit_code": exit_code,
        "git": asdict(state),
    }
    append_receipt(store, receipt)
    return exit_code, receipt


def run_suite(
    checks: Sequence[CheckDefinition],
    *,
    cwd: Path,
    store: Path,
    fail_fast: bool = False,
) -> tuple[int, list[dict[str, Any]]]:
    suite_exit = 0
    results: list[dict[str, Any]] = []
    for check in checks:
        exit_code, receipt = run_check(
            name=check.name,
            command=check.command,
            cwd=cwd,
            store=store,
        )
        results.append(
            {
                "name": check.name,
                "command": list(check.command),
                "exit_code": exit_code,
                "receipt": receipt,
            }
        )
        if exit_code != 0 and suite_exit == 0:
            suite_exit = exit_code
            if fail_fast:
                break
    return suite_exit, results


def _coerce_path_map(raw: Any) -> dict[str, str] | None:
    if not isinstance(raw, dict):
        return None
    coerced: dict[str, str] = {}
    for key, value in raw.items():
        if isinstance(key, str) and isinstance(value, str):
            coerced[key] = value
    return coerced


def _changed_paths(recorded: Any, current: dict[str, str]) -> list[str]:
    recorded_map = _coerce_path_map(recorded)
    if recorded_map is None:
        return []

    changed: list[str] = []
    for path in sorted(set(recorded_map) | set(current)):
        if recorded_map.get(path) != current.get(path):
            changed.append(path)
    return changed


def assess_receipts(
    receipts: Iterable[dict[str, Any]],
    *,
    current: GitState,
    max_age_hours: float,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    receipt_list = list(receipts)
    integrity = audit_receipts(receipt_list)
    latest: dict[str, tuple[int, dict[str, Any]]] = {}
    for index, receipt in enumerate(receipt_list):
        name = str(receipt.get("name", "unnamed"))
        current_latest = latest.get(name)
        if (
            current_latest is None
            or receipt.get("started_at", "")
            > current_latest[1].get("started_at", "")
        ):
            latest[name] = (index, receipt)

    now = now or datetime.now(timezone.utc)
    assessed: list[dict[str, Any]] = []
    for name in sorted(latest):
        index, receipt = latest[name]
        reasons: list[str] = []
        if integrity[index]["state"] == "invalid":
            reasons.append("receipt chain invalid")
        if receipt.get("exit_code") != 0:
            reasons.append("failed")

        try:
            started_at = datetime.fromisoformat(receipt["started_at"])
            age_hours = (now - started_at).total_seconds() / 3600
        except (KeyError, TypeError, ValueError):
            age_hours = float("inf")
            reasons.append("invalid timestamp")
        if max_age_hours > 0 and age_hours > max_age_hours:
            reasons.append("expired")

        recorded = receipt.get("git", {})
        working_tree_paths = {"tracked": [], "untracked": []}
        if recorded.get("available") != current.available:
            reasons.append("repository changed")
        elif current.available:
            if recorded.get("head") != current.head:
                reasons.append("commit changed")
            if recorded.get("fingerprint") != current.fingerprint:
                working_tree_paths = {
                    "tracked": _changed_paths(
                        recorded.get("tracked_changes"),
                        current.tracked_changes,
                    ),
                    "untracked": _changed_paths(
                        recorded.get("untracked_files"),
                        current.untracked_files,
                    ),
                }
                reasons.append("working tree changed")

        assessed.append(
            {
                "name": name,
                "state": "valid" if not reasons else "stale",
                "reasons": reasons,
                "age_hours": round(age_hours, 2),
                "working_tree_paths": working_tree_paths,
                "receipt": receipt,
            }
        )
    return assessed

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


SCHEMA_VERSION = 1
DEFAULT_STORE = Path(".proofrun/receipts.jsonl")


@dataclass(frozen=True)
class GitState:
    available: bool
    head: str | None
    branch: str | None
    dirty: bool
    fingerprint: str | None


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


def git_state(cwd: Path) -> GitState:
    cwd = cwd.resolve()
    probe = _git(cwd, "rev-parse", "--is-inside-work-tree", check=False)
    if probe.returncode != 0 or probe.stdout.strip() != b"true":
        return GitState(False, None, None, False, None)

    head_result = _git(cwd, "rev-parse", "HEAD", check=False)
    head = head_result.stdout.decode().strip() if head_result.returncode == 0 else None
    branch_result = _git(cwd, "branch", "--show-current", check=False)
    branch = branch_result.stdout.decode().strip() or None

    digest = hashlib.sha256()
    digest.update((head or "unborn").encode())
    for args in (("diff", "--binary"), ("diff", "--cached", "--binary")):
        result = _git(cwd, *args, check=False)
        digest.update(result.stdout)

    untracked = _untracked_files(cwd)
    for path in sorted(untracked):
        relative = path.relative_to(cwd).as_posix()
        digest.update(relative.encode())
        try:
            digest.update(path.read_bytes())
        except (OSError, IsADirectoryError):
            digest.update(b"<unreadable>")

    status = _git(cwd, "status", "--porcelain", "--untracked-files=all", check=False)
    dirty = bool(status.stdout.strip())
    return GitState(True, head, branch, dirty, digest.hexdigest())


def ensure_store(store: Path) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    if store.parent.name == ".proofrun":
        ignore = store.parent / ".gitignore"
        if not ignore.exists():
            # Keep runtime evidence, including this ignore file, out of the
            # repository state that receipts fingerprint.
            ignore.write_text("*\n", encoding="utf-8")


def append_receipt(store: Path, receipt: dict[str, Any]) -> None:
    ensure_store(store)
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


def assess_receipts(
    receipts: Iterable[dict[str, Any]],
    *,
    current: GitState,
    max_age_hours: float,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for receipt in receipts:
        name = str(receipt.get("name", "unnamed"))
        if name not in latest or receipt.get("started_at", "") > latest[name].get("started_at", ""):
            latest[name] = receipt

    now = now or datetime.now(timezone.utc)
    assessed: list[dict[str, Any]] = []
    for name in sorted(latest):
        receipt = latest[name]
        reasons: list[str] = []
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
        if recorded.get("available") != current.available:
            reasons.append("repository changed")
        elif current.available:
            if recorded.get("head") != current.head:
                reasons.append("commit changed")
            if recorded.get("fingerprint") != current.fingerprint:
                reasons.append("working tree changed")

        assessed.append(
            {
                "name": name,
                "state": "valid" if not reasons else "stale",
                "reasons": reasons,
                "age_hours": round(age_hours, 2),
                "receipt": receipt,
            }
        )
    return assessed

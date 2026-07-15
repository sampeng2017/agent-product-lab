from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import uuid
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Iterable, Iterator, Sequence

if os.name == "nt":  # pragma: no cover - exercised on Windows
    import msvcrt
else:  # pragma: no cover - platform branch, locking behavior tested below
    import fcntl


SCHEMA_VERSION = 4
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
    cwd: str = "."
    env: tuple[tuple[str, str], ...] = ()


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


def _lock_file(handle: BinaryIO, *, shared: bool) -> None:
    if os.name == "nt":  # pragma: no cover - exercised on Windows
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        # msvcrt has no shared lock mode, so readers take the same short
        # exclusive lock on Windows.
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
    else:
        mode = fcntl.LOCK_SH if shared else fcntl.LOCK_EX
        fcntl.flock(handle.fileno(), mode)


def _unlock_file(handle: BinaryIO) -> None:
    if os.name == "nt":  # pragma: no cover - exercised on Windows
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


@contextmanager
def receipt_store_lock(store: Path, *, shared: bool = False) -> Iterator[None]:
    """Coordinate receipt access using a sibling OS-managed lock file."""
    ensure_store(store)
    lock_path = store.with_name(f"{store.name}.lock")
    with lock_path.open("a+b") as handle:
        _lock_file(handle, shared=shared)
        try:
            yield
        finally:
            _unlock_file(handle)


def append_receipt(store: Path, receipt: dict[str, Any]) -> None:
    with receipt_store_lock(store):
        previous = _load_receipts_unlocked(store)
        receipt["schema_version"] = SCHEMA_VERSION
        receipt["previous_hash"] = receipt_digest(previous[-1]) if previous else None
        receipt.pop("receipt_hash", None)
        receipt["receipt_hash"] = receipt_digest(receipt)
        with store.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, sort_keys=True) + "\n")


def load_receipts(store: Path) -> list[dict[str, Any]]:
    if not store.parent.exists():
        return []
    with receipt_store_lock(store, shared=True):
        return _load_receipts_unlocked(store)


def _load_receipts_unlocked(store: Path) -> list[dict[str, Any]]:
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
    execution_cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> tuple[int, dict[str, Any]]:
    if not command:
        raise ValueError("a command is required")

    ensure_store(store)
    repository_cwd = cwd.resolve()
    effective_cwd = (execution_cwd or repository_cwd).resolve()
    env_overrides = dict(sorted((env or {}).items()))
    process_env = os.environ.copy()
    process_env.update(env_overrides)
    started_at = datetime.now(timezone.utc)
    start = time.monotonic()
    try:
        completed = subprocess.run(
            list(command),
            cwd=effective_cwd,
            env=process_env,
            check=False,
        )
        exit_code = completed.returncode
    except FileNotFoundError:
        exit_code = 127
    duration_ms = round((time.monotonic() - start) * 1000)
    state = git_state(repository_cwd)
    try:
        receipt_cwd = effective_cwd.relative_to(repository_cwd).as_posix() or "."
    except ValueError:
        receipt_cwd = str(effective_cwd)
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "id": uuid.uuid4().hex[:12],
        "name": name,
        "command": list(command),
        "context": {"cwd": receipt_cwd, "env": env_overrides},
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
    jobs: int = 1,
) -> tuple[int, list[dict[str, Any]]]:
    if jobs < 1:
        raise ValueError("jobs must be one or greater")

    repository_cwd = cwd.resolve()
    execution_contexts: list[tuple[CheckDefinition, Path, dict[str, str]]] = []
    for check in checks:
        execution_cwd = (repository_cwd / check.cwd).resolve()
        try:
            execution_cwd.relative_to(repository_cwd)
        except ValueError as exc:
            raise ValueError(
                f"check {check.name!r} cwd escapes the repository: {check.cwd}"
            ) from exc
        if not execution_cwd.is_dir():
            raise ValueError(
                f"check {check.name!r} cwd is not a directory: {check.cwd}"
            )
        execution_contexts.append((check, execution_cwd, dict(check.env)))

    def run_context(
        context: tuple[CheckDefinition, Path, dict[str, str]],
    ) -> dict[str, Any]:
        check, execution_cwd, env = context
        exit_code, receipt = run_check(
            name=check.name,
            command=check.command,
            cwd=cwd,
            store=store,
            execution_cwd=execution_cwd,
            env=env,
        )
        return {
            "name": check.name,
            "command": list(check.command),
            "exit_code": exit_code,
            "receipt": receipt,
        }

    completed: dict[int, dict[str, Any]] = {}
    next_index = 0
    stop_scheduling = False
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        pending: dict[Future[dict[str, Any]], int] = {}

        def fill_workers() -> None:
            nonlocal next_index
            while (
                not stop_scheduling
                and len(pending) < jobs
                and next_index < len(execution_contexts)
            ):
                future = executor.submit(run_context, execution_contexts[next_index])
                pending[future] = next_index
                next_index += 1

        fill_workers()
        while pending:
            done, _ = wait(pending, return_when=FIRST_COMPLETED)
            batch_failed = False
            for future in done:
                index = pending.pop(future)
                result = future.result()
                completed[index] = result
                batch_failed = batch_failed or result["exit_code"] != 0
            if fail_fast and batch_failed:
                stop_scheduling = True
            fill_workers()

    results = [completed[index] for index in sorted(completed)]
    suite_exit = next(
        (item["exit_code"] for item in results if item["exit_code"] != 0),
        0,
    )
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

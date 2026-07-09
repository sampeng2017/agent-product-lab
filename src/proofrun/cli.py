from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Sequence

from .core import DEFAULT_STORE, assess_receipts, git_state, load_receipts, run_check


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="proofrun",
        description="Record verification receipts tied to repository state.",
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=DEFAULT_STORE,
        help="receipt store (default: .proofrun/receipts.jsonl)",
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    run = subparsers.add_parser("run", help="run a command and record its receipt")
    run.add_argument("--name", required=True, help="stable name for this check")
    run.add_argument("command", nargs=argparse.REMAINDER, help="command after --")

    status = subparsers.add_parser("status", help="show whether latest receipts still apply")
    status.add_argument("--max-age-hours", type=float, default=24.0)
    status.add_argument("--json", action="store_true")

    history = subparsers.add_parser("history", help="show recent receipts")
    history.add_argument("--limit", type=int, default=10)
    history.add_argument("--json", action="store_true")
    return parser


def _resolve_store(cwd: Path, store: Path) -> Path:
    return store if store.is_absolute() else cwd / store


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cwd = Path.cwd()
    store = _resolve_store(cwd, args.store)

    if args.action == "run":
        command = list(args.command)
        if command and command[0] == "--":
            command = command[1:]
        if not command:
            print("proofrun: a command is required after --", file=sys.stderr)
            return 2
        exit_code, receipt = run_check(name=args.name, command=command, cwd=cwd, store=store)
        result = "passed" if exit_code == 0 else f"failed ({exit_code})"
        print(
            f"proofrun: {args.name} {result}; receipt {receipt['id']} "
            f"({receipt['duration_ms']} ms)"
        )
        return exit_code

    try:
        receipts = load_receipts(store)
    except ValueError as exc:
        print(f"proofrun: {exc}", file=sys.stderr)
        return 2

    if args.action == "status":
        assessed = assess_receipts(
            receipts,
            current=git_state(cwd),
            max_age_hours=args.max_age_hours,
        )
        if args.json:
            print(json.dumps(assessed, indent=2, sort_keys=True))
        elif not assessed:
            print("No verification receipts yet.")
        else:
            for item in assessed:
                details = ", ".join(item["reasons"]) or "evidence applies"
                print(f"{item['state'].upper():5}  {item['name']}: {details}")
        return 0

    limit = max(args.limit, 0)
    recent = receipts[-limit:] if limit else []
    if args.json:
        print(json.dumps(recent, indent=2, sort_keys=True))
    elif not recent:
        print("No verification receipts yet.")
    else:
        for receipt in reversed(recent):
            result = "pass" if receipt.get("exit_code") == 0 else "fail"
            command = shlex.join(receipt.get("command", []))
            print(f"{receipt.get('started_at')}  {result:4}  {receipt.get('name')}  {command}")
    return 0

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .core import Limits, SnapshotError, run_check


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="residuecheck",
        description="Report bounded filesystem residue left by one command.",
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="tree to inspect")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATH",
        help="exclude a relative path prefix (repeatable; .git is always excluded)",
    )
    parser.add_argument("--max-entries", type=_nonnegative, default=10_000)
    parser.add_argument("--max-file-bytes", type=_nonnegative, default=16 * 1024 * 1024)
    parser.add_argument("--max-total-bytes", type=_nonnegative, default=256 * 1024 * 1024)
    parser.add_argument("--max-changes", type=_nonnegative, default=100)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="command and arguments after --")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    command = arguments.command
    if command[:1] == ["--"]:
        command = command[1:]
    exclusions = [".git", *arguments.exclude]
    try:
        result = run_check(
            arguments.root,
            command,
            exclusions=exclusions,
            limits=Limits(
                max_entries=arguments.max_entries,
                max_file_bytes=arguments.max_file_bytes,
                max_total_bytes=arguments.max_total_bytes,
            ),
        )
    except SnapshotError as exc:
        print(f"residuecheck: {exc}", file=sys.stderr)
        return 2

    command_label = "passed" if result.command_exit == 0 else "failed"
    print(f"Command: {command_label} (exit {result.command_exit})")
    visible = result.changes[: arguments.max_changes]
    for change in visible:
        print(f"{change.kind.upper()} {change.path}")
    hidden = len(result.changes) - len(visible)
    counts = {
        kind: sum(change.kind == kind for change in result.changes)
        for kind in ("created", "modified", "removed")
    }
    if result.changes:
        suffix = f"; {hidden} more not shown" if hidden else ""
        print(
            "Result: "
            f"{len(result.changes)} changes "
            f"({counts['created']} created, {counts['modified']} modified, "
            f"{counts['removed']} removed){suffix}"
        )
    else:
        print(
            "Result: clean; "
            f"{result.after.entries} entries and {result.after.bytes_hashed} bytes inspected"
        )
    return int(result.command_exit != 0 or bool(result.changes))


def _nonnegative(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be nonnegative")
    return parsed

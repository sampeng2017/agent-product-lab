from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import InspectionError, check_sources, parse_target


def positive_integer(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="grammarcheck",
        description="Check Python sources against an explicit older grammar.",
    )
    parser.add_argument("paths", nargs="*", help="relative .py files or directories")
    parser.add_argument("--root", default=".", help="source root (default: current directory)")
    parser.add_argument("--target", required=False, help="target grammar, such as 3.10")
    parser.add_argument("--max-files", type=positive_integer, default=10_000)
    parser.add_argument("--max-file-bytes", type=positive_integer, default=1024 * 1024)
    parser.add_argument("--max-total-bytes", type=positive_integer, default=50 * 1024 * 1024)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.target is None:
        print("grammarcheck: error: --target is required", file=sys.stderr)
        return 2
    try:
        target = parse_target(arguments.target)
        result = check_sources(
            Path(arguments.root),
            arguments.paths,
            target,
            max_files=arguments.max_files,
            max_file_bytes=arguments.max_file_bytes,
            max_total_bytes=arguments.max_total_bytes,
        )
    except InspectionError as exc:
        print(f"grammarcheck: error: {exc}", file=sys.stderr)
        return 2

    incompatible = {finding.path: finding for finding in result.findings}
    for path in result.files:
        finding = incompatible.get(path)
        if finding is None:
            print(f"PASS {path}")
        else:
            print(
                f"INCOMPATIBLE {path}:{finding.line}:{finding.column}: "
                f"{finding.message}"
            )
    compatible_count = len(result.files) - len(result.findings)
    print(
        f"Result: target Python {target[0]}.{target[1]}; "
        f"{compatible_count} compatible, {len(result.findings)} incompatible, "
        f"{len(result.files)} files, {result.total_bytes} bytes"
    )
    return 0 if not result.findings else 1

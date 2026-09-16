from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from . import __version__
from .core import ContractError, load_contract, run_contract


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wheelcontract",
        description="Verify installed Python CLI wheel behavior from TOML.",
    )
    parser.add_argument(
        "manifest",
        nargs="?",
        default="wheelcontract.toml",
        help="contract path (default: wheelcontract.toml)",
    )
    parser.add_argument(
        "--wheel",
        type=Path,
        help="use this prebuilt wheel instead of [artifact].source",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        contract = load_contract(Path(args.manifest))
        if args.wheel is not None:
            wheel = args.wheel.resolve()
            if not wheel.is_file() or wheel.suffix != ".whl":
                raise ContractError(
                    f"--wheel must name an existing .whl file: {args.wheel}"
                )
            contract = replace(contract, artifact_source=wheel)
        results = run_contract(contract)
    except ContractError as exc:
        print(f"wheelcontract: error: {exc}", file=sys.stderr)
        return 2

    passed = 0
    for result in results:
        if result.passed:
            passed += 1
            print(f"PASS {result.name}")
            continue
        print(f"FAIL {result.name}")
        for error in result.errors:
            print(f"  - {error}")
        if result.stdout:
            print(f"  stdout: {_preview(result.stdout)}")
        if result.stderr:
            print(f"  stderr: {_preview(result.stderr)}")
    failed = len(results) - passed
    print(f"Result: {passed} passed, {failed} failed, {len(results)} total")
    return 0 if failed == 0 else 1


def _preview(value: str, limit: int = 240) -> str:
    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1] + "…"

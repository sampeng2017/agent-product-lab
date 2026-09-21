from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import ContractError, check_wheel, load_contract


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wheelfact",
        description="Check an existing wheel against an exact structure contract.",
    )
    parser.add_argument("contract", help="TOML contract path")
    parser.add_argument("wheel", help="existing .whl artifact")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        contract = load_contract(Path(arguments.contract))
        results = check_wheel(Path(arguments.wheel), contract)
    except ContractError as exc:
        print(f"wheelfact: error: {exc}", file=sys.stderr)
        return 2

    matched = 0
    for result in results:
        if result.matched:
            matched += 1
            print(f"PASS {result.label}: {result.actual!r}")
        elif result.actual is None:
            print(f"MISSING {result.label}: expected {result.expected!r}")
        elif result.expected is None:
            print(f"UNEXPECTED {result.label}: {result.actual!r}")
        else:
            print(
                f"MISMATCH {result.label}: was {result.actual!r}; "
                f"expected {result.expected!r}"
            )
    mismatched = len(results) - matched
    print(f"Result: {matched} matched, {mismatched} mismatched, {len(results)} total")
    return 0 if mismatched == 0 else 1

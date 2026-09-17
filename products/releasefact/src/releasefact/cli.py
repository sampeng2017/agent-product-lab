from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import ContractError, check_contract, load_contract


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="releasefact",
        description="Check explicit release-version claims against canonical TOML.",
    )
    parser.add_argument(
        "contract",
        nargs="?",
        default="releasefact.toml",
        help="contract path (default: releasefact.toml)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        contract = load_contract(Path(args.contract))
        canonical, results = check_contract(contract)
    except ContractError as exc:
        print(f"releasefact: error: {exc}", file=sys.stderr)
        return 2

    matched = 0
    for result in results:
        location = f"{result.path}:{result.line}"
        if result.matched:
            matched += 1
            print(f"PASS {result.name}: {location} = {result.actual!r}")
        else:
            print(
                f"DRIFT {result.name}: {location} is {result.actual!r}; "
                f"expected {result.expected!r}"
            )
    drifted = len(results) - matched
    print(
        f"Result: canonical {canonical!r}; {matched} matched, "
        f"{drifted} drifted, {len(results)} total"
    )
    return 0 if drifted == 0 else 1

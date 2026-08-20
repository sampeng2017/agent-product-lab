from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .core import PROFILES, TargetInspection, inspect_targets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentscope",
        description="Explain which repository instructions apply to a target path.",
    )
    parser.add_argument("targets", nargs="*", help="files or directories (default: .)")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root (default: current directory)",
    )
    parser.add_argument(
        "--profile",
        choices=PROFILES,
        default="agents-md",
        help="instruction discovery behavior to model (default: agents-md)",
    )
    parser.add_argument("--json", action="store_true", help="emit versioned JSON")
    parser.add_argument(
        "--require-instructions",
        action="store_true",
        help="exit 1 when any target has no applied instructions",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        inspected = inspect_targets(args.root, args.targets, profile=args.profile)
    except (OSError, ValueError) as exc:
        print(f"agentscope: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(_json_result(args.root, args.profile, inspected), indent=2))
    else:
        _print_human(args.root, args.profile, inspected)

    if args.require_instructions and any(item.applied_count == 0 for item in inspected):
        return 1
    return 0


def _json_result(
    root: Path, profile: str, inspected: Sequence[TargetInspection]
) -> dict[str, object]:
    applied = sum(item.applied_count for item in inspected)
    return {
        "schema_version": 1,
        "profile": profile,
        "root": str(root.resolve()),
        "target_count": len(inspected),
        "applied_source_count": applied,
        "targets": [item.to_dict() for item in inspected],
    }


def _print_human(
    root: Path, profile: str, inspected: Sequence[TargetInspection]
) -> None:
    print(f"AgentScope: {profile} profile in {root.resolve()}")
    for item in inspected:
        print(f"\n{item.target}: {item.applied_count} applied")
        if not item.sources:
            print("  no instruction files discovered")
            continue
        for source in item.sources:
            print(
                f"  {source.state.upper():8} {source.path} "
                f"[{source.kind}] — {source.reason}"
            )

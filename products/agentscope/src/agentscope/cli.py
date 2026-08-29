from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .core import (
    PROFILES,
    TargetComparison,
    TargetInspection,
    compare_targets,
    inspect_targets,
    resolve_instruction_directories,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentscope",
        description="Explain which repository instructions apply to a target path.",
        epilog="Run 'agentscope compare --help' to compare all supported profiles.",
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
    parser.add_argument(
        "--cwd",
        type=Path,
        default=Path("."),
        help="Copilot session directory; relative paths use root (default: root)",
    )
    parser.add_argument(
        "--instructions-dir",
        type=Path,
        action="append",
        default=[],
        help="additional contained Copilot instruction directory (repeatable)",
    )
    parser.add_argument("--json", action="store_true", help="emit versioned JSON")
    parser.add_argument(
        "--require-instructions",
        action="store_true",
        help="exit 1 when any target has no applied instructions",
    )
    parser.add_argument(
        "--fail-on-invalid-references",
        action="store_true",
        help="exit 1 when any target has an invalid reference in its profile",
    )
    parser.add_argument(
        "--fail-on-invalid-sources",
        action="store_true",
        help="exit 1 when any target has an invalid instruction source",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def build_compare_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentscope compare",
        description="Compare applied instruction sources across supported profiles.",
    )
    parser.add_argument("targets", nargs="*", help="files or directories (default: .)")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root (default: current directory)",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        default=Path("."),
        help="Copilot session directory; relative paths use root (default: root)",
    )
    parser.add_argument(
        "--instructions-dir",
        type=Path,
        action="append",
        default=[],
        help="additional contained Copilot instruction directory (repeatable)",
    )
    parser.add_argument("--json", action="store_true", help="emit versioned JSON")
    parser.add_argument(
        "--fail-on-divergence",
        action="store_true",
        help="exit 1 when any target has profile-specific applied sources",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(argv) if argv is not None else sys.argv[1:]
    if arguments and arguments[0] == "compare":
        return _compare_main(arguments[1:])

    args = build_parser().parse_args(arguments)
    try:
        inspected = inspect_targets(
            args.root,
            args.targets,
            profile=args.profile,
            cwd=args.cwd,
            instruction_dirs=args.instructions_dir,
        )
    except (OSError, ValueError) as exc:
        print(f"agentscope: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                _json_result(
                    args.root,
                    args.cwd,
                    args.instructions_dir,
                    args.profile,
                    inspected,
                ),
                indent=2,
            )
        )
    else:
        _print_human(
            args.root,
            args.cwd,
            args.instructions_dir,
            args.profile,
            inspected,
        )

    missing_required = args.require_instructions and any(
        item.applied_count == 0 for item in inspected
    )
    invalid_references = args.fail_on_invalid_references and any(
        item.invalid_reference_count > 0 for item in inspected
    )
    invalid_sources = args.fail_on_invalid_sources and any(
        item.invalid_source_count > 0 for item in inspected
    )
    if missing_required or invalid_references or invalid_sources:
        return 1
    return 0


def _compare_main(argv: Sequence[str]) -> int:
    args = build_compare_parser().parse_args(argv)
    try:
        compared = compare_targets(
            args.root,
            args.targets,
            cwd=args.cwd,
            instruction_dirs=args.instructions_dir,
        )
    except (OSError, ValueError) as exc:
        print(f"agentscope: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                _comparison_json_result(
                    args.root, args.cwd, args.instructions_dir, compared
                ),
                indent=2,
            )
        )
    else:
        _print_comparison(args.root, args.cwd, args.instructions_dir, compared)

    if args.fail_on_divergence and any(item.divergent for item in compared):
        return 1
    return 0


def _json_result(
    root: Path,
    cwd: Path,
    instruction_dirs: Sequence[Path],
    profile: str,
    inspected: Sequence[TargetInspection],
) -> dict[str, object]:
    applied = sum(item.applied_count for item in inspected)
    invalid_references = sum(item.invalid_reference_count for item in inspected)
    invalid_sources = sum(item.invalid_source_count for item in inspected)
    return {
        "schema_version": 5,
        "profile": profile,
        "root": str(root.resolve()),
        "session_directory": _session_label(root, cwd),
        "additional_instruction_directories": _instruction_directory_labels(
            root, instruction_dirs
        ),
        "target_count": len(inspected),
        "applied_source_count": applied,
        "invalid_reference_count": invalid_references,
        "invalid_source_count": invalid_sources,
        "targets": [item.to_dict() for item in inspected],
    }


def _print_human(
    root: Path,
    cwd: Path,
    instruction_dirs: Sequence[Path],
    profile: str,
    inspected: Sequence[TargetInspection],
) -> None:
    applied = sum(item.applied_count for item in inspected)
    invalid_references = sum(item.invalid_reference_count for item in inspected)
    invalid_sources = sum(item.invalid_source_count for item in inspected)
    print(f"AgentScope: {profile} profile in {root.resolve()}")
    print(f"Session directory: {_session_label(root, cwd)}")
    labels = _instruction_directory_labels(root, instruction_dirs)
    print(
        "Additional instruction directories: "
        + (", ".join(labels) if labels else "none")
    )
    print(
        f"Targets: {len(inspected)}; applied sources: {applied}; "
        f"invalid sources: {invalid_sources}; invalid references: {invalid_references}"
    )
    for item in inspected:
        reference_label = (
            "invalid reference"
            if item.invalid_reference_count == 1
            else "invalid references"
        )
        print(
            f"\n{item.target}: {item.applied_count} applied, "
            f"{item.invalid_source_count} invalid, "
            f"{item.invalid_reference_count} {reference_label}"
        )
        if not item.sources:
            print("  no instruction files discovered")
            continue
        for source in item.sources:
            print(
                f"  {source.state.upper():8} {source.path} "
                f"[{source.kind}] — {source.reason}"
            )


def _comparison_json_result(
    root: Path,
    cwd: Path,
    instruction_dirs: Sequence[Path],
    compared: Sequence[TargetComparison],
) -> dict[str, object]:
    return {
        "schema_version": 3,
        "root": str(root.resolve()),
        "session_directory": _session_label(root, cwd),
        "additional_instruction_directories": _instruction_directory_labels(
            root, instruction_dirs
        ),
        "profiles": list(PROFILES),
        "target_count": len(compared),
        "divergent_target_count": sum(item.divergent for item in compared),
        "targets": [item.to_dict() for item in compared],
    }


def _print_comparison(
    root: Path,
    cwd: Path,
    instruction_dirs: Sequence[Path],
    compared: Sequence[TargetComparison],
) -> None:
    print(f"AgentScope comparison in {root.resolve()}")
    print(f"Session directory: {_session_label(root, cwd)}")
    labels = _instruction_directory_labels(root, instruction_dirs)
    print(
        "Additional instruction directories: "
        + (", ".join(labels) if labels else "none")
    )
    for item in compared:
        state = "DIVERGENT" if item.divergent else "CONSISTENT"
        print(f"\n{item.target}: {state}")
        if not item.common_sources and not any(
            profile.applied_sources for profile in item.profiles
        ):
            print("  no applied instruction sources in either profile")
            continue

        _print_source_group("COMMON", item.common_sources)
        for profile in item.profiles:
            _print_source_group(
                f"{profile.profile} ONLY", profile.unique_sources
            )


def _print_source_group(label: str, sources: Sequence[str]) -> None:
    print(f"  {label} ({len(sources)})")
    for source in sources:
        print(f"    {source}")


def _session_label(root: Path, cwd: Path) -> str:
    candidate = cwd if cwd.is_absolute() else root.resolve() / cwd
    relative = candidate.resolve().relative_to(root.resolve())
    return "." if relative == Path(".") else relative.as_posix()


def _instruction_directory_labels(
    root: Path, directories: Sequence[Path]
) -> list[str]:
    resolved_root = root.resolve()
    labels: list[str] = []
    for directory in resolve_instruction_directories(resolved_root, directories):
        relative = directory.relative_to(resolved_root)
        labels.append("." if relative == Path(".") else relative.as_posix())
    return labels

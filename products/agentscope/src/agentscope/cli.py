from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .core import (
    PROFILES,
    ModularRuleCoverage,
    TargetComparison,
    TargetInspection,
    _matches,
    compare_targets,
    cover_targets,
    inspect_targets,
    resolve_instruction_directories,
)


COMPACT_TARGET_COLUMNS = 12


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentscope",
        description="Explain which repository instructions apply to a target path.",
        epilog=(
            "Run 'agentscope compare --help' to compare profiles or "
            "'agentscope coverage --help' to group modular rules by target."
        ),
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
    parser.add_argument(
        "--fail-on-ignored-sources",
        action="store_true",
        help="exit 1 when any target has an ignored path instruction",
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
        "--require-instructions",
        action="store_true",
        help="exit 1 when any target is unguided across all profiles",
    )
    parser.add_argument(
        "--fail-on-divergence",
        action="store_true",
        help="exit 1 when any target has profile-specific applied sources",
    )
    parser.add_argument(
        "--fail-on-invalid-references",
        action="store_true",
        help="exit 1 when any target has an invalid reference in any profile",
    )
    parser.add_argument(
        "--fail-on-invalid-sources",
        action="store_true",
        help="exit 1 when any target has an invalid source in any profile",
    )
    parser.add_argument(
        "--fail-on-ignored-sources",
        action="store_true",
        help="exit 1 when any target has an ignored path instruction in any profile",
    )
    return parser


def build_coverage_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentscope coverage",
        description="Group Copilot modular-instruction coverage across targets.",
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
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="emit versioned JSON")
    output.add_argument(
        "--compact",
        action="store_true",
        help="emit a compact human-readable source-by-target matrix",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="PATH-GLOB",
        help=(
            "display modular sources whose repository-relative path matches this "
            "glob (repeatable; human output only)"
        ),
    )
    parser.add_argument(
        "--fail-on-ignored-sources",
        action="store_true",
        help="exit 1 when a discovered modular rule ignores any requested target",
    )
    parser.add_argument(
        "--fail-on-invalid-sources",
        action="store_true",
        help="exit 1 when any discovered modular rule is invalid",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(argv) if argv is not None else sys.argv[1:]
    if arguments and arguments[0] == "compare":
        return _compare_main(arguments[1:])
    if arguments and arguments[0] == "coverage":
        return _coverage_main(arguments[1:])

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
    ignored_sources = args.fail_on_ignored_sources and any(
        item.ignored_source_count > 0 for item in inspected
    )
    if missing_required or invalid_references or invalid_sources or ignored_sources:
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

    missing_required = args.require_instructions and any(
        not item.has_applied_guidance for item in compared
    )
    divergent = args.fail_on_divergence and any(item.divergent for item in compared)
    invalid_references = args.fail_on_invalid_references and any(
        item.invalid_reference_count > 0 for item in compared
    )
    invalid_sources = args.fail_on_invalid_sources and any(
        item.invalid_source_count > 0 for item in compared
    )
    ignored_sources = args.fail_on_ignored_sources and any(
        item.ignored_source_count > 0 for item in compared
    )
    if (
        missing_required
        or divergent
        or invalid_references
        or invalid_sources
        or ignored_sources
    ):
        return 1
    return 0


def _coverage_main(argv: Sequence[str]) -> int:
    parser = build_coverage_parser()
    args = parser.parse_args(argv)
    if args.json and args.source:
        parser.error("--source is only available for human-readable output")
    try:
        covered = cover_targets(
            args.root,
            args.targets,
            cwd=args.cwd,
            instruction_dirs=args.instructions_dir,
        )
    except (OSError, ValueError) as exc:
        print(f"agentscope: {exc}", file=sys.stderr)
        return 2

    targets = args.targets or (Path("."),)
    displayed = _select_coverage_sources(covered, args.source)
    if args.json:
        print(
            json.dumps(
                _coverage_json_result(
                    args.root,
                    args.cwd,
                    args.instructions_dir,
                    targets,
                    covered,
                ),
                indent=2,
            )
        )
    elif args.compact:
        _print_coverage_compact(
            args.root,
            args.cwd,
            args.instructions_dir,
            targets,
            displayed,
            all_covered=covered,
            source_filters=args.source,
        )
    else:
        _print_coverage(
            args.root,
            args.cwd,
            args.instructions_dir,
            targets,
            displayed,
            all_covered=covered,
            source_filters=args.source,
        )

    ignored = args.fail_on_ignored_sources and any(
        item.ignored_target_count > 0 for item in covered
    )
    invalid = args.fail_on_invalid_sources and any(
        item.invalid_target_count > 0 for item in covered
    )
    return 1 if ignored or invalid else 0


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
        "schema_version": 5,
        "root": str(root.resolve()),
        "session_directory": _session_label(root, cwd),
        "additional_instruction_directories": _instruction_directory_labels(
            root, instruction_dirs
        ),
        "profiles": list(PROFILES),
        "target_count": len(compared),
        "divergent_target_count": sum(item.divergent for item in compared),
        "non_applied_source_count": sum(
            item.non_applied_source_count for item in compared
        ),
        "invalid_source_count": sum(
            item.invalid_source_count for item in compared
        ),
        "invalid_reference_count": sum(
            item.invalid_reference_count for item in compared
        ),
        "targets": [item.to_dict() for item in compared],
    }


def _coverage_json_result(
    root: Path,
    cwd: Path,
    instruction_dirs: Sequence[Path],
    targets: Sequence[str | Path],
    covered: Sequence[ModularRuleCoverage],
) -> dict[str, object]:
    target_labels = _target_labels(root, targets)
    return {
        "schema_version": 1,
        "profile": "copilot-cli",
        "root": str(root.resolve()),
        "session_directory": _session_label(root, cwd),
        "additional_instruction_directories": _instruction_directory_labels(
            root, instruction_dirs
        ),
        "target_count": len(target_labels),
        "targets": target_labels,
        "modular_source_count": len(covered),
        "matched_target_count": sum(item.matched_target_count for item in covered),
        "ignored_target_count": sum(item.ignored_target_count for item in covered),
        "invalid_target_count": sum(item.invalid_target_count for item in covered),
        "sources": [item.to_dict() for item in covered],
    }


def _print_coverage(
    root: Path,
    cwd: Path,
    instruction_dirs: Sequence[Path],
    targets: Sequence[str | Path],
    covered: Sequence[ModularRuleCoverage],
    *,
    all_covered: Sequence[ModularRuleCoverage] | None = None,
    source_filters: Sequence[str] = (),
) -> None:
    complete = covered if all_covered is None else all_covered
    _print_coverage_header(root, cwd, instruction_dirs, targets, complete)
    _print_coverage_filter(source_filters, len(covered), len(complete))
    if not covered:
        _print_no_coverage_sources(source_filters)
        return
    for item in covered:
        patterns = ", ".join(item.patterns) if item.patterns else "unavailable"
        print(
            f"\n{item.path}: discovered for {len(item.target_occurrences)}/"
            f"{len(targets)} targets; {item.matched_target_count} matched; "
            f"{item.ignored_target_count} ignored; {item.invalid_target_count} invalid"
        )
        print(f"  applyTo: {patterns}")
        for occurrence in item.target_occurrences:
            print(
                f"  {occurrence.state.upper():7} {occurrence.target} — "
                f"{occurrence.reason}"
            )


def _print_coverage_compact(
    root: Path,
    cwd: Path,
    instruction_dirs: Sequence[Path],
    targets: Sequence[str | Path],
    covered: Sequence[ModularRuleCoverage],
    *,
    all_covered: Sequence[ModularRuleCoverage] | None = None,
    source_filters: Sequence[str] = (),
) -> None:
    complete = covered if all_covered is None else all_covered
    _print_coverage_header(root, cwd, instruction_dirs, targets, complete)
    _print_coverage_filter(source_filters, len(covered), len(complete))
    if not covered:
        _print_no_coverage_sources(source_filters)
        return

    target_labels = _target_labels(root, targets)
    rule_width = max(len("RULE"), len(f"R{len(covered)}"))
    target_width = max(1, len(str(len(target_labels))))
    symbols = {"matched": "M", "ignored": "I", "invalid": "X"}
    rows = [
        (
            f"R{index}",
            {
                occurrence.target: symbols[occurrence.state]
                for occurrence in item.target_occurrences
            },
        )
        for index, item in enumerate(covered, start=1)
    ]

    print("\nCoverage matrix (M=matched, I=ignored, X=invalid, -=not discovered)")
    chunked = len(target_labels) > COMPACT_TARGET_COLUMNS
    for start in range(0, len(target_labels), COMPACT_TARGET_COLUMNS):
        stop = min(start + COMPACT_TARGET_COLUMNS, len(target_labels))
        chunk_targets = target_labels[start:stop]
        if chunked:
            print(f"\nTargets {start + 1}-{stop} of {len(target_labels)}")
        header_cells = [
            f"{index:>{target_width}}" for index in range(start + 1, stop + 1)
        ]
        separator_cells = ["-" * target_width for _ in chunk_targets]
        print(f"{'RULE':<{rule_width}} | " + " | ".join(header_cells))
        print(f"{'-' * rule_width}-+-" + "-+-".join(separator_cells) + "-")
        for rule_label, state_by_target in rows:
            state_cells = [
                f"{state_by_target.get(target, '-'):>{target_width}}"
                for target in chunk_targets
            ]
            print(f"{rule_label:<{rule_width}} | " + " | ".join(state_cells))

    print("\nRules (first-discovery order):")
    for index, item in enumerate(covered, start=1):
        patterns = ", ".join(item.patterns) if item.patterns else "unavailable"
        print(f"  R{index} {item.path} — applyTo: {patterns}")
    print("\nTargets (caller order):")
    for index, target in enumerate(target_labels, start=1):
        print(f"  {index} {target}")
    print("\nUse the default coverage view for occurrence reasons.")


def _select_coverage_sources(
    covered: Sequence[ModularRuleCoverage], source_filters: Sequence[str]
) -> list[ModularRuleCoverage]:
    if not source_filters:
        return list(covered)
    return [
        item
        for item in covered
        if any(_matches(item.path, pattern) for pattern in source_filters)
    ]


def _print_coverage_filter(
    source_filters: Sequence[str], displayed_count: int, total_count: int
) -> None:
    if source_filters:
        print(
            "Source display filter: "
            f"{', '.join(source_filters)}; displaying {displayed_count} of "
            f"{total_count} modular sources (policy gates use all {total_count})"
        )


def _print_no_coverage_sources(source_filters: Sequence[str]) -> None:
    if source_filters:
        print("\nNo modular instruction sources matched the display filter.")
    else:
        print("\nNo modular instruction sources discovered.")


def _print_coverage_header(
    root: Path,
    cwd: Path,
    instruction_dirs: Sequence[Path],
    targets: Sequence[str | Path],
    covered: Sequence[ModularRuleCoverage],
) -> None:
    print(f"AgentScope modular coverage in {root.resolve()}")
    print("Profile: copilot-cli")
    print(f"Session directory: {_session_label(root, cwd)}")
    labels = _instruction_directory_labels(root, instruction_dirs)
    print(
        "Additional instruction directories: "
        + (", ".join(labels) if labels else "none")
    )
    print(
        f"Targets: {len(targets)}; modular sources: {len(covered)}; "
        f"matched: {sum(item.matched_target_count for item in covered)}; "
        f"ignored: {sum(item.ignored_target_count for item in covered)}; "
        f"invalid: {sum(item.invalid_target_count for item in covered)}"
    )


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
    print(
        f"Targets: {len(compared)}; "
        f"unguided targets: {sum(not item.has_applied_guidance for item in compared)}; "
        f"divergent targets: {sum(item.divergent for item in compared)}; "
        "non-applied sources: "
        f"{sum(item.non_applied_source_count for item in compared)}; "
        "invalid sources: "
        f"{sum(item.invalid_source_count for item in compared)}; "
        "invalid references: "
        f"{sum(item.invalid_reference_count for item in compared)}"
    )
    for item in compared:
        if not item.has_applied_guidance:
            state = "UNGUIDED"
        else:
            state = "DIVERGENT" if item.divergent else "CONSISTENT"
        print(
            f"\n{item.target}: {state}; "
            f"{item.non_applied_source_count} non-applied; "
            f"{item.invalid_source_count} invalid; "
            f"{item.invalid_reference_count} invalid references"
        )
        if not item.common_sources and not any(
            profile.applied_sources for profile in item.profiles
        ):
            print("  no applied instruction sources in either profile")
        else:
            _print_source_group("COMMON", item.common_sources)
            for profile in item.profiles:
                _print_source_group(
                    f"{profile.profile} ONLY", profile.unique_sources
                )

        for profile in item.profiles:
            print(
                f"  {profile.profile} NON-APPLIED "
                f"({profile.non_applied_source_count})"
            )
            for source in profile.non_applied_sources:
                print(
                    f"    {source.state.upper()} {source.path} "
                    f"[{source.kind}] — {source.reason}"
                )
            print(
                f"  {profile.profile} DIAGNOSTICS "
                f"({profile.invalid_source_count} invalid; "
                f"{profile.invalid_reference_count} invalid references)"
            )
            for source in profile.invalid_sources:
                print(f"    {source.path} [{source.kind}] — {source.reason}")


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


def _target_labels(root: Path, targets: Sequence[str | Path]) -> list[str]:
    resolved_root = root.resolve()
    labels: list[str] = []
    for target in targets:
        requested = Path(target)
        candidate = requested if requested.is_absolute() else resolved_root / requested
        relative = candidate.resolve(strict=False).relative_to(resolved_root)
        labels.append("." if relative == Path(".") else relative.as_posix())
    return labels

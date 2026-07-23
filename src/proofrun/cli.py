from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Sequence

from .core import (
    CheckDefinition,
    DEFAULT_STORE,
    assess_receipts,
    audit_receipts,
    git_state,
    load_receipts,
    run_check,
    run_suite,
)
from .manifest import load_manifest, select_checks
from .presentation import DEFAULT_PATH_LIMIT, limited_working_tree_paths
from .report import render_markdown_report
from .scaffold import (
    ScaffoldPlan,
    apply_scaffold_plan,
    plan_repository_initialization,
)


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

    init = subparsers.add_parser(
        "init", help="create a starter manifest and optional GitHub Actions workflow"
    )
    init.add_argument(
        "--check-name",
        default="test",
        help="name for the starter check (default: test)",
    )
    init.add_argument(
        "--github-actions",
        action="store_true",
        help="also create .github/workflows/proofrun.yml",
    )
    init.add_argument(
        "--ci-install",
        help="pip requirement used to install ProofRun in the generated workflow",
    )
    init.add_argument(
        "--force",
        action="store_true",
        help="overwrite selected scaffold files",
    )
    init.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and preview the scaffold without writing files",
    )
    init.add_argument(
        "--json",
        action="store_true",
        help="with --dry-run, include exact generated content as JSON",
    )
    init.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="custom check command after --; otherwise detect the project type",
    )

    run = subparsers.add_parser("run", help="run a command and record its receipt")
    run.add_argument("--name", required=True, help="stable name for this check")
    run.add_argument("command", nargs=argparse.REMAINDER, help="command after --")

    status = subparsers.add_parser("status", help="show whether latest receipts still apply")
    status.add_argument("--max-age-hours", type=float, default=24.0)
    status.add_argument(
        "--path-limit",
        type=_nonnegative_int,
        default=DEFAULT_PATH_LIMIT,
        help=f"maximum invalidating paths to display (default: {DEFAULT_PATH_LIMIT})",
    )
    status.add_argument(
        "--require-valid",
        action="store_true",
        help="exit nonzero when any selected proof is stale or missing",
    )
    status.add_argument("--json", action="store_true")
    status.add_argument("names", nargs="*", help="optional check names to assess")

    history = subparsers.add_parser("history", help="show recent receipts")
    history.add_argument("--limit", type=int, default=10)
    history.add_argument("--json", action="store_true")

    audit = subparsers.add_parser("audit", help="verify receipt hashes and chain links")
    audit.add_argument("--json", action="store_true")

    report = subparsers.add_parser("report", help="export current proof as Markdown")
    report.add_argument("--max-age-hours", type=float, default=24.0)
    report.add_argument(
        "--path-limit",
        type=_nonnegative_int,
        default=DEFAULT_PATH_LIMIT,
        help=f"maximum invalidating paths per check (default: {DEFAULT_PATH_LIMIT})",
    )
    report.add_argument(
        "--output",
        type=Path,
        help="write the report to a file instead of standard output",
    )

    verify = subparsers.add_parser("verify", help="run checks defined in a manifest")
    verify.add_argument(
        "--manifest",
        type=Path,
        default=Path("proofrun.toml"),
        help="manifest file (default: proofrun.toml)",
    )
    verify.add_argument("--fail-fast", action="store_true")
    verify.add_argument(
        "--jobs",
        type=_positive_int,
        default=1,
        help="maximum checks to run concurrently (default: 1)",
    )
    verify.add_argument(
        "--json",
        action="store_true",
        help="emit one machine-readable suite result on standard output",
    )
    verify.add_argument("names", nargs="*", help="optional check names to run")
    return parser


def _resolve_store(cwd: Path, store: Path) -> Path:
    return store if store.is_absolute() else cwd / store


def _resolve_path(cwd: Path, path: Path) -> Path:
    return path if path.is_absolute() else cwd / path


def _nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be one or greater")
    return parsed


def _format_status_reasons(item: dict[str, object], *, path_limit: int) -> str:
    reasons = item.get("reasons")
    if not isinstance(reasons, list) or not reasons:
        return "evidence applies"

    shown_paths, omitted = limited_working_tree_paths(
        item.get("working_tree_paths"), path_limit
    )
    changed_paths = shown_paths["tracked"] + shown_paths["untracked"]

    details: list[str] = []
    for reason in reasons:
        if not isinstance(reason, str):
            continue
        if reason == "working tree changed" and (changed_paths or omitted):
            path_details = ", ".join(changed_paths)
            if omitted:
                overflow = f"+{omitted} more"
                path_details = f"{path_details}, {overflow}" if path_details else overflow
            details.append(f"{reason}: {path_details}")
        elif reason == "repository changed during check":
            receipt = item.get("receipt")
            mutation = (
                receipt.get("repository_mutation")
                if isinstance(receipt, dict)
                else None
            )
            mutation_paths = {
                "tracked": mutation.get("tracked_paths", []),
                "untracked": mutation.get("untracked_paths", []),
            } if isinstance(mutation, dict) else None
            shown, mutation_omitted = limited_working_tree_paths(
                mutation_paths, path_limit
            )
            paths = shown["tracked"] + shown["untracked"]
            path_details = ", ".join(paths)
            if mutation_omitted:
                overflow = f"+{mutation_omitted} more"
                path_details = f"{path_details}, {overflow}" if path_details else overflow
            if isinstance(mutation, dict) and mutation.get("head_changed"):
                path_details = (
                    f"{path_details}, commit changed"
                    if path_details
                    else "commit changed"
                )
            details.append(f"{reason}: {path_details}" if path_details else reason)
        else:
            details.append(reason)
    return ", ".join(details) or "evidence applies"


def _select_status_items(
    assessed: list[dict[str, object]], names: Sequence[str]
) -> list[dict[str, object]]:
    if not names:
        return assessed

    by_name = {str(item["name"]): item for item in assessed}
    selected: list[dict[str, object]] = []
    for name in names:
        item = by_name.get(name)
        if item is not None:
            selected.append(item)
            continue
        selected.append(
            {
                "name": name,
                "state": "missing",
                "reasons": ["no receipt"],
                "age_hours": None,
                "working_tree_paths": {"tracked": [], "untracked": []},
                "receipt": None,
            }
        )
    return selected


def _verify_json_summary(
    checks: Sequence[CheckDefinition],
    results: list[dict[str, object]],
    suite_exit: int,
) -> dict[str, object]:
    serialized_results: list[dict[str, object]] = []
    passed = 0
    for item in results:
        result = dict(item)
        result["state"] = "passed" if item["exit_code"] == 0 else "failed"
        serialized_results.append(result)
        if item["exit_code"] == 0:
            passed += 1

    skipped_checks = [check.name for check in checks[len(results) :]]
    return {
        "schema_version": 1,
        "state": "passed" if suite_exit == 0 else "failed",
        "exit_code": suite_exit,
        "selected_count": len(checks),
        "executed_count": len(results),
        "passed_count": passed,
        "failed_count": len(results) - passed,
        "skipped_count": len(skipped_checks),
        "skipped_checks": skipped_checks,
        "results": serialized_results,
    }


def _result_label(exit_code: int, receipt: dict[str, object]) -> str:
    mutation = receipt.get("repository_mutation")
    if isinstance(mutation, dict) and mutation.get("detected") is True:
        command_exit = receipt.get("command_exit_code", exit_code)
        return f"rejected: repository changed (command exit {command_exit})"
    return "passed" if exit_code == 0 else f"failed ({exit_code})"


def _init_preview(
    plan: ScaffoldPlan, cwd: Path, *, force: bool
) -> dict[str, object]:
    preset = plan.preset
    return {
        "schema_version": 1,
        "mode": "dry-run",
        "force": force,
        "check": {
            "name": plan.check_name,
            "command": list(plan.command),
            "source": "detected" if preset is not None else "explicit",
            "preset": preset.label if preset is not None else None,
            "package_manager": (
                preset.package_manager if preset is not None else None
            ),
        },
        "targets": [
            {
                "path": target.path.relative_to(cwd).as_posix(),
                "action": target.action,
                "content": target.content,
            }
            for target in plan.targets
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cwd = Path.cwd()
    store = _resolve_store(cwd, args.store)

    if args.action == "init":
        if args.json and not args.dry_run:
            print("proofrun: --json requires --dry-run for init", file=sys.stderr)
            return 2
        command = list(args.command)
        if command and command[0] == "--":
            command = command[1:]
        try:
            plan = plan_repository_initialization(
                cwd,
                check_name=args.check_name,
                command=command or None,
                github_actions=args.github_actions,
                ci_install=args.ci_install,
                force=args.force,
            )
        except (OSError, ValueError) as exc:
            print(f"proofrun: {exc}", file=sys.stderr)
            return 2
        if args.dry_run and args.json:
            print(
                json.dumps(
                    _init_preview(plan, cwd, force=args.force),
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        if plan.preset is not None:
            print(
                f"proofrun: detected {plan.preset.label}; "
                f"using {shlex.join(plan.command)}"
            )
        else:
            print(f"proofrun: using explicit command {shlex.join(plan.command)}")
        if args.dry_run:
            for target in plan.targets:
                print(
                    f"proofrun: would {target.action} "
                    f"{target.path.relative_to(cwd)}"
                )
            return 0
        try:
            written = apply_scaffold_plan(plan)
        except (OSError, ValueError) as exc:
            print(f"proofrun: {exc}", file=sys.stderr)
            return 2
        for path in written:
            print(f"proofrun: wrote {path.relative_to(cwd)}")
        return 0

    if args.action == "run":
        command = list(args.command)
        if command and command[0] == "--":
            command = command[1:]
        if not command:
            print("proofrun: a command is required after --", file=sys.stderr)
            return 2
        exit_code, receipt = run_check(name=args.name, command=command, cwd=cwd, store=store)
        result = _result_label(exit_code, receipt)
        print(
            f"proofrun: {args.name} {result}; receipt {receipt['id']} "
            f"({receipt['duration_ms']} ms)"
        )
        return exit_code

    if args.action == "verify":
        manifest_path = _resolve_path(cwd, args.manifest)
        try:
            checks = select_checks(load_manifest(manifest_path), args.names)
        except ValueError as exc:
            print(f"proofrun: {exc}", file=sys.stderr)
            return 2

        try:
            suite_exit, results = run_suite(
                checks,
                cwd=cwd,
                store=store,
                fail_fast=args.fail_fast,
                jobs=args.jobs,
                command_stdout=sys.stderr if args.json else None,
            )
        except ValueError as exc:
            print(f"proofrun: {exc}", file=sys.stderr)
            return 2
        if args.json:
            print(
                json.dumps(
                    _verify_json_summary(checks, results, suite_exit),
                    indent=2,
                    sort_keys=True,
                )
            )
            return suite_exit

        passed = 0
        for item in results:
            result = _result_label(item["exit_code"], item["receipt"])
            print(
                f"proofrun: {item['name']} {result}; receipt {item['receipt']['id']} "
                f"({item['receipt']['duration_ms']} ms)"
            )
            if item["exit_code"] == 0:
                passed += 1

        summary = f"{passed}/{len(results)} checks passed"
        if len(results) != len(checks):
            summary += f", {len(checks) - len(results)} skipped after failure"
        print(f"proofrun: suite {'passed' if suite_exit == 0 else 'failed'}; {summary}")
        return suite_exit

    try:
        receipts = load_receipts(store)
    except ValueError as exc:
        print(f"proofrun: {exc}", file=sys.stderr)
        return 2

    if args.action == "status":
        assessed = _select_status_items(
            assess_receipts(
                receipts,
                current=git_state(cwd),
                max_age_hours=args.max_age_hours,
            ),
            args.names,
        )
        if args.json:
            print(json.dumps(assessed, indent=2, sort_keys=True))
        elif not assessed:
            print("No verification receipts yet.")
        else:
            for item in assessed:
                details = _format_status_reasons(item, path_limit=args.path_limit)
                print(f"{item['state'].upper():5}  {item['name']}: {details}")
        if args.require_valid and (
            not assessed or any(item["state"] != "valid" for item in assessed)
        ):
            return 1
        return 0

    if args.action == "audit":
        audited = audit_receipts(receipts)
        invalid = sum(item["state"] == "invalid" for item in audited)
        unsealed = sum(item["state"] == "unsealed" for item in audited)
        summary = {
            "state": "invalid" if invalid else "valid",
            "receipt_count": len(audited),
            "sealed_count": len(audited) - unsealed,
            "verified_count": len(audited) - invalid - unsealed,
            "unsealed_count": unsealed,
            "invalid_count": invalid,
            "receipts": audited,
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        elif not audited:
            print("No verification receipts yet.")
        else:
            for item in audited:
                details = "; ".join(item["issues"])
                if item["state"] == "unsealed":
                    details = "legacy receipt (not sealed)"
                elif not details:
                    details = "hash and link verified"
                print(
                    f"{item['state'].upper():8}  #{item['index']} "
                    f"{item['name']}: {details}"
                )
            print(
                f"proofrun: audit {summary['state']}; {summary['receipt_count']} receipts, "
                f"{summary['unsealed_count']} legacy unsealed"
            )
        return 1 if invalid else 0

    if args.action == "report":
        report = render_markdown_report(
            receipts,
            current=git_state(cwd),
            max_age_hours=args.max_age_hours,
            path_limit=args.path_limit,
        )
        if args.output:
            output = _resolve_path(cwd, args.output)
            try:
                output.write_text(report, encoding="utf-8")
            except OSError as exc:
                print(f"proofrun: could not write report: {exc}", file=sys.stderr)
                return 2
            print(f"proofrun: wrote Markdown report to {output}")
        else:
            print(report, end="")
        invalid = any(item["state"] == "invalid" for item in audit_receipts(receipts))
        return 1 if invalid else 0

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

"""Replay a stale-proof workflow in a disposable repository using installed ProofRun."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class DemoError(RuntimeError):
    pass


def run(command: list[str], root: Path, environment: dict[str, str], expected: int = 0):
    result = subprocess.run(
        command, cwd=root, env=environment, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=60,
    )
    if result.returncode != expected:
        raise DemoError(
            f"Expected exit {expected}, got {result.returncode}: "
            f"{result.stdout}{result.stderr}"
        )
    return result


def _proofrun_launcher(installed_command: bool) -> list[str]:
    if not installed_command:
        return [sys.executable, "-B", "-m", "proofrun"]
    command = shutil.which("proofrun")
    if command is None:
        raise DemoError("ProofRun command not found on PATH; install it or use the default Python-environment route.")
    # Capture the selected command before changing the working directory or
    # putting the caller's Python first on PATH for the fixture's test command.
    return [str(Path(command).resolve())]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--installed-command", action="store_true",
        help="use the proofrun command on PATH instead of this Python's proofrun module",
    )
    args = parser.parse_args(argv)
    if shutil.which("git") is None:
        print("Install Git and put it on PATH before running this example.", file=sys.stderr)
        return 2
    try:
        launcher = _proofrun_launcher(args.installed_command)
    except DemoError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.installed_command:
        print(f"Using ProofRun command: {launcher[0]}", flush=True)
    environment = dict(os.environ)
    for key in list(environment):
        if key in ("PYTHONPATH", "PYTHONHOME") or key.startswith("GIT_"):
            environment.pop(key, None)
    environment["PATH"] = str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", "")
    try:
        with tempfile.TemporaryDirectory(prefix="proofrun-example-") as temporary:
            base = Path(temporary)
            root = base / "project"
            shutil.copytree(
                Path(__file__).resolve().parent / "project", root,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            hint = (
                "The selected ProofRun command could not run; check its installation."
                if args.installed_command else
                "Install ProofRun in this Python environment first; see docs/INSTALLATION.md."
            )
            try:
                prerequisite = subprocess.run(
                    [*launcher, "--help"], cwd=root, env=environment,
                    capture_output=True, timeout=60,
                )
            except (OSError, subprocess.TimeoutExpired):
                print(hint, file=sys.stderr)
                return 2
            if prerequisite.returncode:
                print(hint, file=sys.stderr)
                return 2
            run(["git", "init", "-q"], root, environment)
            run(["git", "add", "."], root, environment)
            hooks = base / "empty-hooks"
            hooks.mkdir()
            run([
                "git", "-c", "user.name=ProofRun example",
                "-c", "user.email=example@example.invalid",
                "-c", "commit.gpgSign=false", "-c", f"core.hooksPath={hooks}",
                "commit", "-qm", "Record example baseline",
            ], root, environment)

            def proofrun(*arguments: str, expected: int = 0):
                print("$ proofrun " + " ".join(arguments), flush=True)
                result = run([*launcher, *arguments], root, environment, expected)
                print(result.stdout + result.stderr, end="", flush=True)
                print(f"Exit: {result.returncode}", flush=True)
                return result

            def check_state(expected: str, tracked: list[str]):
                result = run(
                    [*launcher, "status", "--json", "unit"], root, environment,
                )
                items = json.loads(result.stdout)
                if (
                    len(items) != 1 or items[0]["state"] != expected
                    or items[0]["working_tree_paths"]["tracked"] != tracked
                ):
                    raise DemoError(f"Unexpected status; wanted {expected} for {tracked}")

            print("1. Verify the original code and check its evidence.", flush=True)
            proofrun("verify", "unit")
            proofrun("status", "--require-valid", "unit")
            check_state("valid", [])

            print("\n2. Change calculator.py from value * 2 to value + value.", flush=True)
            (root / "calculator.py").write_text(
                "def double(value):\n    return value + value\n", encoding="utf-8",
            )
            proofrun("status", "--require-valid", "unit", expected=1)
            check_state("stale", ["calculator.py"])
            print("The earlier passing tests do not cover the edited working tree.", flush=True)

            print("\n3. Run verification again for the edited code.", flush=True)
            proofrun("verify", "unit")
            proofrun("status", "--require-valid", "unit")
            check_state("valid", [])
            proofrun("audit")
            print("\nPASS: valid -> stale -> valid; all changes stayed in the temporary copy.")
        return 0
    except (DemoError, OSError, subprocess.TimeoutExpired, ValueError, KeyError) as exc:
        print(f"Example failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

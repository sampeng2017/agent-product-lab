"""Replay an instruction-scope correction with installed AgentScope."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


RULE = ".github/instructions/api.instructions.md"
TARGETS = ["api/app.py", "web/app.py"]


def fingerprint(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*") if path.is_file()
    }


def main() -> int:
    environment = dict(os.environ)
    for key in ("PYTHONPATH", "PYTHONHOME"):
        environment.pop(key, None)
    launcher = [sys.executable, "-B", "-m", "agentscope"]
    try:
        with tempfile.TemporaryDirectory(prefix="agentscope-example-") as temporary:
            root = Path(temporary) / "project"
            shutil.copytree(
                Path(__file__).resolve().parent / "project", root,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            prerequisite = subprocess.run(
                [*launcher, "--version"], cwd=root, env=environment,
                capture_output=True, timeout=30,
            )
            if prerequisite.returncode:
                print("Install AgentScope in this Python environment; see docs/INSTALLATION.md.", file=sys.stderr)
                return 2

            def inspect(arguments: list[str], expected: int = 0, show: bool = True):
                before = fingerprint(root)
                result = subprocess.run(
                    [*launcher, *arguments], cwd=root, env=environment,
                    capture_output=True, text=True, encoding="utf-8",
                    errors="replace", timeout=30,
                )
                if result.returncode != expected:
                    raise ValueError(f"Expected exit {expected}, got {result.returncode}: {result.stdout}{result.stderr}")
                if fingerprint(root) != before:
                    raise ValueError("Inspection changed the example files")
                if show:
                    print("$ agentscope " + " ".join(arguments), flush=True)
                    print(result.stdout + result.stderr, end="", flush=True)
                    print(f"Exit: {result.returncode}", flush=True)
                return result.stdout

            base = ["--profile", "copilot-cli", "--root", "."]

            def check_sources(state: str, applied: int, expected_exit: int):
                payload = json.loads(inspect(
                    [*base, "--fail-on-ignored-sources", "--json", TARGETS[0]],
                    expected_exit, show=False,
                ))
                sources = payload["targets"][0]["sources"]
                rule = [source for source in sources if source["path"] == RULE]
                if (
                    payload["schema_version"] != 5
                    or payload["invalid_source_count"] != 0
                    or payload["applied_source_count"] != applied
                    or len(rule) != 1 or rule[0]["state"] != state
                ):
                    raise ValueError(f"Expected rule {state} with {applied} applied sources")

            def check_coverage(expected: dict[str, str]):
                payload = json.loads(inspect(
                    ["coverage", "--root", ".", "--json", *TARGETS], show=False,
                ))
                sources = payload["sources"]
                if payload["schema_version"] != 1 or len(sources) != 1:
                    raise ValueError("Expected one modular rule in coverage")
                actual = {item["target"]: item["state"] for item in sources[0]["target_occurrences"]}
                if actual != expected:
                    raise ValueError(f"Unexpected rule coverage: {actual}")

            print("1. The API rule points at web files instead of API files.", flush=True)
            inspect([*base, TARGETS[0]])
            inspect([*base, "--fail-on-ignored-sources", TARGETS[0]], expected=1)
            check_sources("ignored", 1, 1)
            inspect(["coverage", "--compact", "--root", ".", *TARGETS])
            check_coverage({TARGETS[0]: "ignored", TARGETS[1]: "matched"})

            print('\n2. Change applyTo from "web/**/*.py" to "api/**/*.py" in the temporary copy.', flush=True)
            rule = root / RULE
            rule.write_text(rule.read_text(encoding="utf-8").replace('"web/**/*.py"', '"api/**/*.py"'), encoding="utf-8")
            inspect([*base, "--fail-on-ignored-sources", TARGETS[0]])
            check_sources("applied", 2, 0)
            inspect(["coverage", "--compact", "--root", ".", *TARGETS])
            check_coverage({TARGETS[0]: "matched", TARGETS[1]: "ignored"})
            print("\nPASS: ignored API rule -> corrected scope; inspections left files unchanged.")
        return 0
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError) as exc:
        print(f"Example failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

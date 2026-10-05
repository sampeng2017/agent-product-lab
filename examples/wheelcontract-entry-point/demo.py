"""Show passing source tests with a missing installed console command."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def main() -> int:
    try:
        backend_version = version("setuptools")
        if int(backend_version.split(".", 1)[0]) < 77:
            raise ValueError("old build backend")
    except (PackageNotFoundError, ValueError):
        print('Install the example build backend with python -m pip install "setuptools>=77".', file=sys.stderr)
        return 2

    environment = dict(os.environ)
    for key in ("PYTHONPATH", "PYTHONHOME"):
        environment.pop(key, None)
    launcher = [sys.executable, "-B", "-m", "wheelcontract"]
    try:
        with tempfile.TemporaryDirectory(prefix="wheelcontract-example-") as temporary:
            root = Path(temporary)
            environment["PIP_CACHE_DIR"] = str(root / "pip-cache")
            environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
            fixture = Path(__file__).resolve().parent
            shutil.copytree(
                fixture / "project", root / "project",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.egg-info", "build", "dist"),
            )
            shutil.copy2(fixture / "wheelcontract.toml", root / "wheelcontract.toml")
            prerequisite = subprocess.run(
                [*launcher, "--version"], cwd=root, env=environment,
                capture_output=True, timeout=30,
            )
            if prerequisite.returncode:
                print("Install WheelContract in this Python environment; see docs/INSTALLATION.md.", file=sys.stderr)
                return 2

            def run(command: list[str], expected: int, cwd: Path, env: dict[str, str]):
                result = subprocess.run(
                    command, cwd=cwd, env=env, capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=120,
                )
                if result.returncode != expected:
                    raise ValueError(f"Expected exit {expected}, got {result.returncode}: {result.stdout}{result.stderr}")
                print(result.stdout + result.stderr, end="", flush=True)
                print(f"Exit: {result.returncode}", flush=True)
                return result.stdout

            print("1. Source behavior tests pass before the package exposes a command.", flush=True)
            source_environment = {**environment, "PYTHONPATH": str(root / "project" / "src")}
            run(
                [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
                0, root / "project", source_environment,
            )

            print("\n2. Check the built wheel in an isolated installed environment.", flush=True)
            print("$ wheelcontract wheelcontract.toml", flush=True)
            output = run([*launcher, "wheelcontract.toml"], 1, root, environment)
            if output.count("installed command not found: release-demo") != 2 or "Result: 0 passed, 2 failed, 2 total" not in output:
                raise ValueError("The expected missing-command diagnosis was absent")

            print("\n3. Add the missing project.scripts entry in the temporary copy.", flush=True)
            project = root / "project" / "pyproject.toml"
            project.write_text(
                project.read_text(encoding="utf-8")
                + '\n[project.scripts]\nrelease-demo = "release_demo.cli:main"\n',
                encoding="utf-8",
            )
            print("$ wheelcontract wheelcontract.toml", flush=True)
            output = run([*launcher, "wheelcontract.toml"], 0, root, environment)
            if "PASS greeting" not in output or "PASS version" not in output or "Result: 2 passed, 0 failed, 2 total" not in output:
                raise ValueError("The corrected artifact did not pass both cases")
            print("\nPASS: source tests passed -> installed command missing -> packaging corrected.")
        return 0
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        print(f"Example failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

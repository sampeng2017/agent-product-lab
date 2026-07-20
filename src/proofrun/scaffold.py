from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


MANIFEST_PATH = Path("proofrun.toml")
WORKFLOW_PATH = Path(".github/workflows/proofrun.yml")
CHECK_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


@dataclass(frozen=True)
class ProjectPreset:
    label: str
    command: tuple[str, ...]


def _python_preset(root: Path) -> ProjectPreset | None:
    tests = root / "tests"
    if not tests.is_dir():
        return None

    pytest_markers = [root / "pytest.ini", root / "conftest.py", tests / "conftest.py"]
    for config in (root / "pyproject.toml", root / "setup.cfg", root / "tox.ini"):
        if not config.exists():
            continue
        try:
            config_text = config.read_text(encoding="utf-8").lower()
        except OSError:
            continue
        if "pytest" in config_text:
            pytest_markers.append(config)
    if any(path.exists() for path in pytest_markers):
        return ProjectPreset("Python (pytest)", ("python", "-m", "pytest"))
    return ProjectPreset(
        "Python (unittest)",
        ("python", "-m", "unittest", "discover", "-s", "tests", "-v"),
    )


def detect_project_preset(root: Path) -> ProjectPreset:
    candidates = [
        preset
        for preset in (
            _python_preset(root),
            ProjectPreset("Node.js", ("npm", "test"))
            if (root / "package.json").is_file()
            else None,
            ProjectPreset("Rust", ("cargo", "test"))
            if (root / "Cargo.toml").is_file()
            else None,
            ProjectPreset("Go", ("go", "test", "./..."))
            if (root / "go.mod").is_file()
            else None,
        )
        if preset is not None
    ]
    if not candidates:
        raise ValueError(
            "could not detect a test command; provide one after -- "
            "(for example: proofrun init -- python -m pytest)"
        )
    if len(candidates) > 1:
        labels = ", ".join(preset.label for preset in candidates)
        raise ValueError(
            f"multiple project types detected ({labels}); provide a command after --"
        )
    return candidates[0]


def _manifest_text(check_name: str, command: Sequence[str]) -> str:
    serialized = ", ".join(json.dumps(part, ensure_ascii=False) for part in command)
    return f"[checks.{check_name}]\ncommand = [{serialized}]\n"


def _workflow_text(ci_install: str) -> str:
    install_requirement = shlex.quote(ci_install)
    return f"""name: ProofRun evidence

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: \"3.12\"

      - name: Install ProofRun
        run: python -m pip install {install_requirement}

      - name: Run structured verification
        run: proofrun verify --json > \"$RUNNER_TEMP/proofrun-results.json\"

      - name: Publish proof summary
        if: always()
        run: |
          report_exit=0
          proofrun report --output \"$RUNNER_TEMP/proofrun-report.md\" || report_exit=$?
          cat \"$RUNNER_TEMP/proofrun-report.md\" >> \"$GITHUB_STEP_SUMMARY\"
          exit \"$report_exit\"

      - name: Upload proof evidence
        if: always()
        uses: actions/upload-artifact@v7
        with:
          name: proofrun-evidence
          path: |
            ${{{{ runner.temp }}}}/proofrun-results.json
            ${{{{ runner.temp }}}}/proofrun-report.md
          if-no-files-found: error
          retention-days: 14

      - name: Enforce valid proof
        if: always()
        run: |
          proofrun audit
          proofrun status --require-valid
"""


def initialize_repository(
    root: Path,
    *,
    check_name: str,
    command: Sequence[str] | None,
    github_actions: bool,
    ci_install: str | None,
    force: bool,
) -> tuple[list[Path], ProjectPreset | None]:
    if not CHECK_NAME_PATTERN.fullmatch(check_name):
        raise ValueError("check name may contain only letters, numbers, '_' and '-'")
    if github_actions and not ci_install:
        raise ValueError(
            "--github-actions requires --ci-install with a pip requirement for ProofRun"
        )
    if ci_install is not None and not github_actions:
        raise ValueError("--ci-install requires --github-actions")
    if ci_install is not None and (
        not ci_install.strip() or "\0" in ci_install or "\n" in ci_install
    ):
        raise ValueError("--ci-install must be a non-empty, single-line pip requirement")

    preset: ProjectPreset | None = None
    selected_command = tuple(command or ())
    if not selected_command:
        preset = detect_project_preset(root)
        selected_command = preset.command
    if not all(
        isinstance(part, str) and part and "\0" not in part
        for part in selected_command
    ):
        raise ValueError("the check command must contain non-empty arguments")

    targets: list[tuple[Path, str]] = [
        (root / MANIFEST_PATH, _manifest_text(check_name, selected_command))
    ]
    if github_actions:
        assert ci_install is not None
        targets.append((root / WORKFLOW_PATH, _workflow_text(ci_install)))

    invalid_targets: list[Path] = []
    for path, _ in targets:
        if path.exists() and not path.is_file():
            invalid_targets.append(path.relative_to(root))
            continue
        existing_parent = path.parent
        while not existing_parent.exists() and existing_parent != root:
            existing_parent = existing_parent.parent
        if not existing_parent.is_dir():
            invalid_targets.append(path.relative_to(root))
    if invalid_targets:
        names = ", ".join(path.as_posix() for path in invalid_targets)
        raise ValueError(f"scaffold targets are not writable files: {names}")

    conflicts = [path.relative_to(root) for path, _ in targets if path.exists()]
    if conflicts and not force:
        names = ", ".join(path.as_posix() for path in conflicts)
        raise ValueError(f"refusing to overwrite existing files: {names}")

    written: list[Path] = []
    for path, content in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written, preset

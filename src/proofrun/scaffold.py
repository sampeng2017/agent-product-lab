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
    package_manager: str | None = None
    package_manager_declared: bool = False
    has_lockfile: bool = False


@dataclass(frozen=True)
class ScaffoldTarget:
    path: Path
    content: str
    action: str


@dataclass(frozen=True)
class ScaffoldPlan:
    root: Path
    check_name: str
    command: tuple[str, ...]
    preset: ProjectPreset | None
    targets: tuple[ScaffoldTarget, ...]


NODE_COMMANDS = {
    "npm": ("npm", "test"),
    "pnpm": ("pnpm", "test"),
    "yarn": ("yarn", "test"),
    "bun": ("bun", "run", "test"),
}

NODE_LOCKFILES = {
    "npm": ("package-lock.json", "npm-shrinkwrap.json"),
    "pnpm": ("pnpm-lock.yaml",),
    "yarn": ("yarn.lock",),
    "bun": ("bun.lock", "bun.lockb"),
}


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


def _declared_node_package_manager(package: dict[str, object]) -> str | None:
    declaration = package.get("packageManager")
    if declaration is None:
        return None
    if not isinstance(declaration, str) or not declaration.strip():
        raise ValueError("package.json packageManager must be a non-empty string")

    manager = declaration.strip().partition("@")[0]
    if manager not in NODE_COMMANDS:
        supported = ", ".join(NODE_COMMANDS)
        raise ValueError(
            f"unsupported Node package manager {manager!r}; supported: {supported}; "
            "or provide a command after --"
        )
    return manager


def _locked_node_package_manager(root: Path) -> str | None:
    detected = [
        manager
        for manager, names in NODE_LOCKFILES.items()
        if any((root / name).is_file() for name in names)
    ]
    if len(detected) > 1:
        raise ValueError(
            "multiple Node package managers detected from lockfiles "
            f"({', '.join(detected)}); provide a command after --"
        )
    return detected[0] if detected else None


def _node_preset(root: Path) -> ProjectPreset | None:
    package_path = root / "package.json"
    if not package_path.is_file():
        return None
    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read package.json: {exc}") from exc
    if not isinstance(package, dict):
        raise ValueError("package.json must contain a JSON object")

    scripts = package.get("scripts")
    test_script = scripts.get("test") if isinstance(scripts, dict) else None
    if not isinstance(test_script, str) or not test_script.strip():
        raise ValueError(
            "package.json has no runnable test script; provide a command after --"
        )
    if "error: no test specified" in test_script.lower():
        raise ValueError(
            "package.json still has the placeholder test script; "
            "provide a command after --"
        )

    declared_manager = _declared_node_package_manager(package)
    manager = declared_manager or _locked_node_package_manager(root) or "npm"
    has_lockfile = any(
        (root / name).is_file() for name in NODE_LOCKFILES[manager]
    )
    return ProjectPreset(
        f"Node.js ({manager})",
        NODE_COMMANDS[manager],
        package_manager=manager,
        package_manager_declared=declared_manager is not None,
        has_lockfile=has_lockfile,
    )


def detect_project_preset(root: Path) -> ProjectPreset:
    candidates = [
        preset
        for preset in (
            _python_preset(root),
            _node_preset(root),
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


def _node_workflow_steps(preset: ProjectPreset | None) -> str:
    if preset is None or preset.package_manager is None:
        return ""

    manager = preset.package_manager
    if manager == "bun":
        install_command = "bun ci" if preset.has_lockfile else "bun install"
        return f"""
      - name: Set up Bun
        uses: oven-sh/setup-bun@v2

      - name: Install project dependencies
        run: {install_command}
"""

    install_commands = {
        "npm": "npm ci" if preset.has_lockfile else "npm install",
        "pnpm": (
            "pnpm install --frozen-lockfile"
            if preset.has_lockfile
            else "pnpm install"
        ),
        "yarn": (
            "yarn install --frozen-lockfile"
            if preset.has_lockfile
            else "yarn install"
        ),
    }
    manager_setup = ""
    if manager == "pnpm":
        manager_setup = """
      - name: Set up pnpm
        uses: pnpm/action-setup@v6
"""
        if not preset.package_manager_declared:
            manager_setup += """        with:
          version: latest
"""
    elif manager == "yarn":
        manager_setup = """
      - name: Enable Corepack
        run: corepack enable
"""

    return f"""
      - name: Set up Node.js
        uses: actions/setup-node@v6
        with:
          node-version: "24"
          package-manager-cache: false
{manager_setup}
      - name: Install project dependencies
        run: {install_commands[manager]}
"""


def _workflow_text(ci_install: str, preset: ProjectPreset | None) -> str:
    install_requirement = shlex.quote(ci_install)
    project_setup = _node_workflow_steps(preset)
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
{project_setup}

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


def plan_repository_initialization(
    root: Path,
    *,
    check_name: str,
    command: Sequence[str] | None,
    github_actions: bool,
    ci_install: str | None,
    force: bool,
) -> ScaffoldPlan:
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

    target_contents: list[tuple[Path, str]] = [
        (root / MANIFEST_PATH, _manifest_text(check_name, selected_command))
    ]
    if github_actions:
        assert ci_install is not None
        target_contents.append(
            (root / WORKFLOW_PATH, _workflow_text(ci_install, preset))
        )

    invalid_targets: list[Path] = []
    for path, _ in target_contents:
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

    conflicts = [
        path.relative_to(root) for path, _ in target_contents if path.exists()
    ]
    if conflicts and not force:
        names = ", ".join(path.as_posix() for path in conflicts)
        raise ValueError(f"refusing to overwrite existing files: {names}")

    return ScaffoldPlan(
        root=root,
        check_name=check_name,
        command=selected_command,
        preset=preset,
        targets=tuple(
            ScaffoldTarget(
                path=path,
                content=content,
                action="overwrite" if path.exists() else "create",
            )
            for path, content in target_contents
        ),
    )


def apply_scaffold_plan(plan: ScaffoldPlan) -> list[Path]:
    appeared = [
        target.path.relative_to(plan.root)
        for target in plan.targets
        if target.action == "create" and target.path.exists()
    ]
    if appeared:
        names = ", ".join(path.as_posix() for path in appeared)
        raise ValueError(f"scaffold targets changed after planning: {names}")

    written: list[Path] = []
    for target in plan.targets:
        target.path.parent.mkdir(parents=True, exist_ok=True)
        target.path.write_text(target.content, encoding="utf-8")
        written.append(target.path)
    return written


def initialize_repository(
    root: Path,
    *,
    check_name: str,
    command: Sequence[str] | None,
    github_actions: bool,
    ci_install: str | None,
    force: bool,
) -> tuple[list[Path], ProjectPreset | None]:
    plan = plan_repository_initialization(
        root,
        check_name=check_name,
        command=command,
        github_actions=github_actions,
        ci_install=ci_install,
        force=force,
    )
    return apply_scaffold_plan(plan), plan.preset

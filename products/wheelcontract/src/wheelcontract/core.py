from __future__ import annotations

import ast
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised through fallback tests
    tomllib = None


_TERMINATION_GRACE_SECONDS = 0.5
_WINDOWS_TASKKILL_TIMEOUT_SECONDS = 5


class ContractError(ValueError):
    """The contract or artifact could not be prepared safely."""


@dataclass(frozen=True)
class Case:
    name: str
    argv: tuple[str, ...]
    expected_exit: int
    stdout_contains: tuple[str, ...]
    stderr_contains: tuple[str, ...]
    json_fields: tuple[tuple[str, object], ...]


@dataclass(frozen=True)
class Contract:
    manifest_path: Path
    artifact_source: Path
    timeout_seconds: int
    max_output_bytes: int
    cases: tuple[Case, ...]


@dataclass(frozen=True)
class CaseResult:
    name: str
    passed: bool
    errors: tuple[str, ...]
    exit_code: int | None
    stdout: str
    stderr: str


def load_contract(path: Path) -> Contract:
    manifest_path = path.resolve()
    if not manifest_path.is_file():
        raise ContractError(f"contract not found: {path}")
    try:
        data = _parse_toml(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ContractError(f"cannot parse {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError("contract must be a TOML document")
    _reject_unknown(data, {"schema_version", "artifact", "run", "case"}, "contract")
    if data.get("schema_version") != 1:
        raise ContractError("schema_version must be 1")

    artifact = _require_table(data.get("artifact"), "[artifact]")
    _reject_unknown(artifact, {"source"}, "[artifact]")
    source = artifact.get("source")
    if not isinstance(source, str) or not source or "\0" in source:
        raise ContractError("[artifact].source must be a non-empty path string")
    source_path = Path(source)
    if not source_path.is_absolute():
        source_path = manifest_path.parent / source_path

    run = data.get("run", {})
    run = _require_table(run, "[run]")
    _reject_unknown(run, {"timeout_seconds", "max_output_bytes"}, "[run]")
    timeout_seconds = _positive_int(run.get("timeout_seconds", 30), "timeout_seconds")
    max_output_bytes = _positive_int(
        run.get("max_output_bytes", 65536), "max_output_bytes"
    )

    raw_cases = data.get("case")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ContractError("contract must define at least one [[case]]")
    cases: list[Case] = []
    names: set[str] = set()
    for index, raw_case in enumerate(raw_cases, start=1):
        label = f"[[case]] #{index}"
        case = _require_table(raw_case, label)
        _reject_unknown(
            case,
            {"name", "argv", "exit", "stdout_contains", "stderr_contains", "json"},
            label,
        )
        name = case.get("name")
        if not isinstance(name, str) or not name:
            raise ContractError(f"{label}.name must be a non-empty string")
        if name in names:
            raise ContractError(f"duplicate case name: {name}")
        names.add(name)
        argv = case.get("argv")
        if not isinstance(argv, list) or not argv or not all(
            isinstance(part, str) and part and "\0" not in part for part in argv
        ):
            raise ContractError(f"case {name!r} argv must be a non-empty string array")
        if Path(argv[0]).name != argv[0]:
            raise ContractError(
                f"case {name!r} command must name an installed entry point or 'python'"
            )
        expected_exit = case.get("exit", 0)
        if isinstance(expected_exit, bool) or not isinstance(expected_exit, int):
            raise ContractError(f"case {name!r} exit must be an integer")
        contains = case.get("stdout_contains", [])
        if not isinstance(contains, list) or not all(
            isinstance(fragment, str) and fragment for fragment in contains
        ):
            raise ContractError(f"case {name!r} stdout_contains must be a string array")
        stderr_contains = case.get("stderr_contains", [])
        if not isinstance(stderr_contains, list) or not all(
            isinstance(fragment, str) and fragment for fragment in stderr_contains
        ):
            raise ContractError(f"case {name!r} stderr_contains must be a string array")
        json_table = case.get("json", {})
        json_table = _require_table(json_table, f"case {name!r} json")
        for key, value in json_table.items():
            if not isinstance(key, str) or not key:
                raise ContractError(f"case {name!r} JSON field names must be strings")
            if not isinstance(value, (str, int, float, bool)):
                raise ContractError(
                    f"case {name!r} JSON expectations must use scalar values"
                )
        cases.append(
            Case(
                name=name,
                argv=tuple(argv),
                expected_exit=expected_exit,
                stdout_contains=tuple(contains),
                stderr_contains=tuple(stderr_contains),
                json_fields=tuple(json_table.items()),
            )
        )
    return Contract(
        manifest_path=manifest_path,
        artifact_source=source_path.resolve(),
        timeout_seconds=timeout_seconds,
        max_output_bytes=max_output_bytes,
        cases=tuple(cases),
    )


def run_contract(contract: Contract) -> tuple[CaseResult, ...]:
    if not contract.artifact_source.exists():
        raise ContractError(f"artifact source not found: {contract.artifact_source}")
    with tempfile.TemporaryDirectory(prefix="wheelcontract-") as temporary:
        root = Path(temporary)
        wheel = _obtain_wheel(contract.artifact_source, root / "wheels")
        environment = root / "environment"
        _run_setup([sys.executable, "-m", "venv", str(environment)], "create environment")
        python = _environment_python(environment)
        _run_setup(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-index",
                "--no-deps",
                str(wheel),
            ],
            "install wheel",
        )
        work = root / "work"
        work.mkdir()
        return tuple(
            _run_case(case, contract, environment, work, root, index)
            for index, case in enumerate(contract.cases, start=1)
        )


def _obtain_wheel(source: Path, wheel_dir: Path) -> Path:
    if source.is_file():
        if source.suffix != ".whl":
            raise ContractError(f"artifact file must be a .whl: {source}")
        return source
    if not source.is_dir():
        raise ContractError(f"artifact source must be a project directory or wheel: {source}")
    wheel_dir.mkdir(parents=True)
    _run_setup(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(wheel_dir),
            str(source),
        ],
        "build wheel",
    )
    wheels = sorted(wheel_dir.glob("*.whl"))
    if len(wheels) != 1:
        raise ContractError(f"build produced {len(wheels)} wheels; expected exactly one")
    return wheels[0]


def _run_setup(argv: list[str], action: str) -> None:
    completed = subprocess.run(
        argv,
        env=_clean_environment(),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode == 0:
        return
    detail = (completed.stderr or completed.stdout).strip()
    if len(detail) > 4000:
        detail = detail[-4000:]
    raise ContractError(f"could not {action} (exit {completed.returncode}): {detail}")


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"nonstandard constant {value}")


def _run_case(
    case: Case,
    contract: Contract,
    environment: Path,
    work: Path,
    temporary_root: Path,
    index: int,
) -> CaseResult:
    command = _installed_command(environment, case.argv[0])
    if command is None:
        return CaseResult(
            name=case.name,
            passed=False,
            errors=(f"installed command not found: {case.argv[0]}",),
            exit_code=None,
            stdout="",
            stderr="",
        )
    manifest_dir = str(contract.manifest_path.parent)
    argv = [str(command)] + [
        part.replace("{manifest_dir}", manifest_dir) for part in case.argv[1:]
    ]
    stdout_path = temporary_root / f"case-{index}.stdout"
    stderr_path = temporary_root / f"case-{index}.stderr"
    environment_variables = _clean_environment()
    timed_out = False
    exit_code: int | None = None
    with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
        process_options: dict[str, Any]
        if os.name == "nt":
            process_options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        else:
            process_options = {"start_new_session": True}
        try:
            process = subprocess.Popen(
                argv,
                cwd=work,
                env=environment_variables,
                stdout=stdout_file,
                stderr=stderr_file,
                **process_options,
            )
        except OSError as exc:
            # A packaged script can exist but have a missing interpreter,
            # invalid executable format, or denied execution permission.
            # This is installed behavior failure, not a suite setup failure.
            detail = (exc.strerror or type(exc).__name__)[:240]
            return CaseResult(
                name=case.name,
                passed=False,
                errors=(
                    f"could not start installed command {case.argv[0]!r}: "
                    f"OS error {exc.errno} ({detail})",
                ),
                exit_code=None,
                stdout="",
                stderr="",
            )
        try:
            exit_code = process.wait(timeout=contract.timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            _terminate_process_tree(process)
    stdout, stdout_size = _read_bounded(stdout_path, contract.max_output_bytes)
    stderr, stderr_size = _read_bounded(stderr_path, contract.max_output_bytes)
    errors: list[str] = []
    if timed_out:
        errors.append(f"timed out after {contract.timeout_seconds}s")
    elif exit_code != case.expected_exit:
        errors.append(f"exit was {exit_code}; expected {case.expected_exit}")
    if stdout_size > contract.max_output_bytes:
        errors.append(
            f"stdout was {stdout_size} bytes; limit is {contract.max_output_bytes}"
        )
    if stderr_size > contract.max_output_bytes:
        errors.append(
            f"stderr was {stderr_size} bytes; limit is {contract.max_output_bytes}"
        )
    for fragment in case.stdout_contains:
        if fragment not in stdout:
            errors.append(f"stdout missing {fragment!r}")
    for fragment in case.stderr_contains:
        if fragment not in stderr:
            errors.append(f"stderr missing {fragment!r}")
    if case.json_fields:
        try:
            document = json.loads(stdout, parse_constant=_reject_json_constant)
        except json.JSONDecodeError as exc:
            errors.append(f"stdout is not JSON: {exc.msg}")
        except RecursionError:
            errors.append("stdout JSON exceeds decoder nesting limit")
        except ValueError as exc:
            errors.append(f"stdout is not JSON: {exc}")
        else:
            if not isinstance(document, dict):
                errors.append("stdout JSON must be an object")
            else:
                for field, expected in case.json_fields:
                    if field not in document:
                        errors.append(f"JSON field {field!r} is missing")
                    elif (
                        document[field] != expected
                        or isinstance(document[field], bool) != isinstance(expected, bool)
                    ):
                        errors.append(
                            f"JSON field {field!r} was {document[field]!r}; expected {expected!r}"
                        )
    return CaseResult(
        name=case.name,
        passed=not errors,
        errors=tuple(errors),
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
    )


def _terminate_process_tree(process: subprocess.Popen[Any]) -> None:
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=_WINDOWS_TASKKILL_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            process.kill()
        _reap_process(process)
        return

    try:
        os.killpg(process.pid, signal.SIGTERM)
    except OSError:
        pass
    # Keep the direct child unreaped during the grace period so its process-group
    # identifier cannot be recycled before residual descendants receive SIGKILL.
    time.sleep(_TERMINATION_GRACE_SECONDS)
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except OSError:
        pass
    _reap_process(process)


def _reap_process(process: subprocess.Popen[Any]) -> None:
    try:
        process.wait(timeout=_TERMINATION_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        try:
            process.wait(timeout=_TERMINATION_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            pass


def _installed_command(environment: Path, name: str) -> Path | None:
    scripts = environment / ("Scripts" if os.name == "nt" else "bin")
    if name == "python":
        return _environment_python(environment)
    candidate = scripts / (f"{name}.exe" if os.name == "nt" else name)
    return candidate if candidate.is_file() else None


def _environment_python(environment: Path) -> Path:
    return environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for name in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONINSPECT"):
        environment.pop(name, None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def _read_bounded(path: Path, limit: int) -> tuple[str, int]:
    size = path.stat().st_size
    with path.open("rb") as handle:
        data = handle.read(limit + 1)
    return data[:limit].decode("utf-8", errors="replace"), size


def _require_table(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a table")
    return value


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ContractError(f"{label} must be a positive integer")
    return value


def _reject_unknown(table: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(table) - allowed)
    if unknown:
        raise ContractError(f"{label} has unsupported keys: {', '.join(unknown)}")


def _parse_toml(text: str) -> dict[str, Any]:
    if tomllib is not None:
        return tomllib.loads(text)
    return _parse_toml_fallback(text)


def _parse_toml_fallback(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current: dict[str, Any] = data
    current_case: dict[str, Any] | None = None
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[artifact]" or line == "[run]":
            name = line[1:-1]
            if name in data:
                raise ValueError(f"duplicate section {line} on line {line_number}")
            current = {}
            data[name] = current
            continue
        if line == "[[case]]":
            current_case = {}
            raw_cases = data.setdefault("case", [])
            if not isinstance(raw_cases, list):
                raise ValueError(f"duplicate key 'case' on line {line_number}")
            raw_cases.append(current_case)
            current = current_case
            continue
        if line == "[case.json]":
            if current_case is None:
                raise ValueError(f"[case.json] before [[case]] on line {line_number}")
            if "json" in current_case:
                raise ValueError(f"duplicate section [case.json] on line {line_number}")
            current = {}
            current_case["json"] = current
            continue
        if line.startswith("["):
            raise ValueError(f"unsupported section on line {line_number}: {line}")
        key, separator, raw_value = line.partition("=")
        if not separator or not key.strip():
            raise ValueError(f"invalid assignment on line {line_number}")
        key = key.strip()
        if key in current:
            raise ValueError(f"duplicate key {key!r} on line {line_number}")
        value = raw_value.strip()
        if value == "true":
            current[key] = True
        elif value == "false":
            current[key] = False
        else:
            try:
                current[key] = ast.literal_eval(value)
            except (SyntaxError, ValueError) as exc:
                raise ValueError(f"invalid value on line {line_number}") from exc
    return data

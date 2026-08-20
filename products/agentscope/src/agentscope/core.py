from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


PROFILES = ("agents-md", "copilot-cli")


@dataclass(frozen=True)
class InstructionSource:
    path: str
    kind: str
    state: str
    reason: str
    patterns: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        item = asdict(self)
        item["patterns"] = list(self.patterns)
        return item


@dataclass(frozen=True)
class TargetInspection:
    target: str
    sources: tuple[InstructionSource, ...]

    @property
    def applied_count(self) -> int:
        return sum(source.state == "applied" for source in self.sources)

    def to_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "applied_count": self.applied_count,
            "sources": [source.to_dict() for source in self.sources],
        }


def inspect_targets(
    root: Path,
    targets: Sequence[str | Path],
    *,
    profile: str = "agents-md",
) -> list[TargetInspection]:
    """Return the instruction sources that a profile applies to each target."""
    if profile not in PROFILES:
        raise ValueError(f"unsupported profile: {profile}")

    resolved_root = root.resolve()
    if not resolved_root.is_dir():
        raise ValueError(f"repository root is not a directory: {root}")

    requested = targets or (Path("."),)
    return [
        _inspect_target(resolved_root, Path(target), profile=profile)
        for target in requested
    ]


def _inspect_target(root: Path, target: Path, *, profile: str) -> TargetInspection:
    candidate = target if target.is_absolute() else root / target
    resolved = candidate.resolve(strict=False)
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"target escapes repository root: {target}") from exc

    target_dir = resolved if resolved.is_dir() else resolved.parent
    if target_dir != root and root not in target_dir.parents:
        raise ValueError(f"target escapes repository root: {target}")

    ancestors = list(_ancestor_directories(root, target_dir))
    if profile == "agents-md":
        sources = _agents_md_sources(root, ancestors)
    else:
        sources = _copilot_cli_sources(root, ancestors, relative.as_posix())

    label = "." if relative == Path(".") else relative.as_posix()
    return TargetInspection(label, tuple(sources))


def _ancestor_directories(root: Path, target_dir: Path) -> Iterable[Path]:
    relative = target_dir.relative_to(root)
    yield root
    current = root
    for part in relative.parts:
        current /= part
        yield current


def _agents_md_sources(
    root: Path, ancestors: Sequence[Path]
) -> list[InstructionSource]:
    files = [directory / "AGENTS.md" for directory in ancestors]
    existing = [path for path in files if path.is_file()]
    if not existing:
        return []

    nearest = existing[-1]
    sources: list[InstructionSource] = []
    for path in existing:
        if path == nearest:
            state = "applied"
            reason = "nearest AGENTS.md for target"
        else:
            state = "shadowed"
            reason = f"shadowed by {_relative(root, nearest)}"
        sources.append(
            InstructionSource(_relative(root, path), "agents-md", state, reason)
        )
    return sources


def _copilot_cli_sources(
    root: Path, ancestors: Sequence[Path], target: str
) -> list[InstructionSource]:
    sources: list[InstructionSource] = []
    repository_instructions = root / ".github" / "copilot-instructions.md"
    if repository_instructions.is_file():
        sources.append(
            InstructionSource(
                _relative(root, repository_instructions),
                "copilot-repository",
                "applied",
                "repository-wide Copilot instructions",
            )
        )

    for directory in ancestors:
        for filename, kind in (
            ("AGENTS.md", "agents-md"),
            ("CLAUDE.md", "claude-md"),
            ("GEMINI.md", "gemini-md"),
        ):
            path = directory / filename
            if path.is_file():
                sources.append(
                    InstructionSource(
                        _relative(root, path),
                        kind,
                        "applied",
                        "combined by Copilot CLI",
                    )
                )

    modular_root = root / ".github" / "instructions"
    if modular_root.is_dir():
        for path in sorted(modular_root.rglob("*.instructions.md")):
            patterns = _read_apply_to_patterns(path)
            if not patterns:
                state = "ignored"
                reason = "missing supported applyTo frontmatter"
            elif any(_matches(target, pattern) for pattern in patterns):
                state = "applied"
                reason = f"applyTo matches {target}"
            else:
                state = "ignored"
                reason = f"applyTo does not match {target}"
            sources.append(
                InstructionSource(
                    _relative(root, path),
                    "copilot-path",
                    state,
                    reason,
                    patterns,
                )
            )
    return sources


def _read_apply_to_patterns(path: Path) -> tuple[str, ...]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return ()
    if not lines or lines[0].strip() != "---":
        return ()

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if not stripped.startswith("applyTo:"):
            continue
        value = stripped.partition(":")[2].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        return tuple(part.strip() for part in value.split(",") if part.strip())
    return ()


def _matches(target: str, pattern: str) -> bool:
    normalized = pattern.replace("\\", "/").lstrip("./")
    expression = ""
    index = 0
    while index < len(normalized):
        character = normalized[index]
        if character == "*":
            if index + 1 < len(normalized) and normalized[index + 1] == "*":
                index += 1
                if index + 1 < len(normalized) and normalized[index + 1] == "/":
                    index += 1
                    expression += "(?:.*/)?"
                else:
                    expression += ".*"
            else:
                expression += "[^/]*"
        elif character == "?":
            expression += "[^/]"
        else:
            expression += re.escape(character)
        index += 1
    return re.fullmatch(expression, target) is not None


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


PROFILES = ("agents-md", "copilot-cli")
REFERENCE_DEPTH_LIMIT = 10
NON_APPLIED_STATES = frozenset(("ignored", "duplicate", "shadowed"))


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
class _ApplyToFrontmatter:
    patterns: tuple[str, ...] = ()
    error: str | None = None


@dataclass(frozen=True)
class TargetInspection:
    target: str
    sources: tuple[InstructionSource, ...]

    @property
    def applied_count(self) -> int:
        return sum(source.state == "applied" for source in self.sources)

    @property
    def invalid_reference_count(self) -> int:
        return sum(
            1
            for source in self.sources
            if source.kind == "copilot-reference" and source.state == "invalid"
        )

    @property
    def invalid_source_count(self) -> int:
        return sum(source.state == "invalid" for source in self.sources)

    @property
    def ignored_source_count(self) -> int:
        return sum(source.state == "ignored" for source in self.sources)

    def to_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "applied_count": self.applied_count,
            "invalid_reference_count": self.invalid_reference_count,
            "invalid_source_count": self.invalid_source_count,
            "sources": [source.to_dict() for source in self.sources],
        }


@dataclass(frozen=True)
class ModularRuleOccurrence:
    target: str
    state: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ModularRuleCoverage:
    path: str
    patterns: tuple[str, ...]
    target_occurrences: tuple[ModularRuleOccurrence, ...]

    @property
    def matched_target_count(self) -> int:
        return sum(item.state == "matched" for item in self.target_occurrences)

    @property
    def ignored_target_count(self) -> int:
        return sum(item.state == "ignored" for item in self.target_occurrences)

    @property
    def invalid_target_count(self) -> int:
        return sum(item.state == "invalid" for item in self.target_occurrences)

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "patterns": list(self.patterns),
            "discovered_target_count": len(self.target_occurrences),
            "matched_target_count": self.matched_target_count,
            "ignored_target_count": self.ignored_target_count,
            "invalid_target_count": self.invalid_target_count,
            "target_occurrences": [
                occurrence.to_dict() for occurrence in self.target_occurrences
            ],
        }


@dataclass(frozen=True)
class ProfileSourceComparison:
    profile: str
    applied_sources: tuple[str, ...]
    unique_sources: tuple[str, ...]
    invalid_sources: tuple[InstructionSource, ...] = ()
    non_applied_sources: tuple[InstructionSource, ...] = ()

    @property
    def non_applied_source_count(self) -> int:
        return len(self.non_applied_sources)

    @property
    def invalid_source_count(self) -> int:
        return len(self.invalid_sources)

    @property
    def ignored_source_count(self) -> int:
        return sum(source.state == "ignored" for source in self.non_applied_sources)

    @property
    def invalid_reference_count(self) -> int:
        return sum(
            source.kind == "copilot-reference" for source in self.invalid_sources
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "applied_source_count": len(self.applied_sources),
            "applied_sources": list(self.applied_sources),
            "unique_sources": list(self.unique_sources),
            "non_applied_source_count": self.non_applied_source_count,
            "non_applied_sources": [
                source.to_dict() for source in self.non_applied_sources
            ],
            "invalid_source_count": self.invalid_source_count,
            "invalid_reference_count": self.invalid_reference_count,
            "invalid_sources": [source.to_dict() for source in self.invalid_sources],
        }


@dataclass(frozen=True)
class TargetComparison:
    target: str
    common_sources: tuple[str, ...]
    profiles: tuple[ProfileSourceComparison, ...]

    @property
    def has_applied_guidance(self) -> bool:
        return any(profile.applied_sources for profile in self.profiles)

    @property
    def divergent(self) -> bool:
        return any(profile.unique_sources for profile in self.profiles)

    @property
    def invalid_source_count(self) -> int:
        return sum(profile.invalid_source_count for profile in self.profiles)

    @property
    def non_applied_source_count(self) -> int:
        return sum(profile.non_applied_source_count for profile in self.profiles)

    @property
    def invalid_reference_count(self) -> int:
        return sum(profile.invalid_reference_count for profile in self.profiles)

    @property
    def ignored_source_count(self) -> int:
        return sum(profile.ignored_source_count for profile in self.profiles)

    def to_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "divergent": self.divergent,
            "non_applied_source_count": self.non_applied_source_count,
            "invalid_source_count": self.invalid_source_count,
            "invalid_reference_count": self.invalid_reference_count,
            "common_sources": list(self.common_sources),
            "profiles": {
                profile.profile: profile.to_dict() for profile in self.profiles
            },
        }


def inspect_targets(
    root: Path,
    targets: Sequence[str | Path],
    *,
    profile: str = "agents-md",
    cwd: str | Path = ".",
    instruction_dirs: Sequence[str | Path] = (),
) -> list[TargetInspection]:
    """Return the instruction sources that a profile applies to each target."""
    if profile not in PROFILES:
        raise ValueError(f"unsupported profile: {profile}")

    resolved_root = root.resolve()
    if not resolved_root.is_dir():
        raise ValueError(f"repository root is not a directory: {root}")
    session_directory = _resolve_session_directory(resolved_root, Path(cwd))
    additional_directories = resolve_instruction_directories(
        resolved_root, instruction_dirs
    )

    requested = targets or (Path("."),)
    return [
        _inspect_target(
            resolved_root,
            Path(target),
            profile=profile,
            session_directory=session_directory,
            instruction_directories=additional_directories,
        )
        for target in requested
    ]


def compare_targets(
    root: Path,
    targets: Sequence[str | Path],
    *,
    cwd: str | Path = ".",
    instruction_dirs: Sequence[str | Path] = (),
) -> list[TargetComparison]:
    """Compare applied paths and retain diagnostic evidence for every profile."""
    inspected_by_profile = {
        profile: inspect_targets(
            root,
            targets,
            profile=profile,
            cwd=cwd,
            instruction_dirs=instruction_dirs,
        )
        for profile in PROFILES
    }
    comparisons: list[TargetComparison] = []

    for index in range(len(inspected_by_profile[PROFILES[0]])):
        inspections = {
            profile: inspected_by_profile[profile][index] for profile in PROFILES
        }
        applied_by_profile = {
            profile: tuple(
                source.path
                for source in inspection.sources
                if source.state == "applied"
            )
            for profile, inspection in inspections.items()
        }
        common = set(applied_by_profile[PROFILES[0]])
        for profile in PROFILES[1:]:
            common.intersection_update(applied_by_profile[profile])

        profile_results = tuple(
            ProfileSourceComparison(
                profile=profile,
                applied_sources=applied_by_profile[profile],
                unique_sources=tuple(
                    path for path in applied_by_profile[profile] if path not in common
                ),
                invalid_sources=tuple(
                    source
                    for source in inspections[profile].sources
                    if source.state == "invalid"
                ),
                non_applied_sources=tuple(
                    source
                    for source in inspections[profile].sources
                    if source.state in NON_APPLIED_STATES
                ),
            )
            for profile in PROFILES
        )
        comparisons.append(
            TargetComparison(
                target=inspections[PROFILES[0]].target,
                common_sources=tuple(
                    path for path in applied_by_profile[PROFILES[0]] if path in common
                ),
                profiles=profile_results,
            )
        )
    return comparisons


def cover_targets(
    root: Path,
    targets: Sequence[str | Path],
    *,
    cwd: str | Path = ".",
    instruction_dirs: Sequence[str | Path] = (),
) -> list[ModularRuleCoverage]:
    """Group Copilot modular-rule outcomes by source across requested targets."""
    inspected = inspect_targets(
        root,
        targets,
        profile="copilot-cli",
        cwd=cwd,
        instruction_dirs=instruction_dirs,
    )
    grouped: dict[str, tuple[tuple[str, ...], list[ModularRuleOccurrence]]] = {}
    for inspection in inspected:
        for source in inspection.sources:
            if source.kind != "copilot-path":
                continue
            patterns, occurrences = grouped.setdefault(
                source.path, (source.patterns, [])
            )
            state = "matched" if source.state == "applied" else source.state
            occurrences.append(
                ModularRuleOccurrence(inspection.target, state, source.reason)
            )

    return [
        ModularRuleCoverage(path, patterns, tuple(occurrences))
        for path, (patterns, occurrences) in grouped.items()
    ]


def _resolve_session_directory(root: Path, cwd: Path) -> Path:
    candidate = cwd if cwd.is_absolute() else root / cwd
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"session directory escapes repository root: {cwd}") from exc
    if not resolved.is_dir():
        raise ValueError(f"session directory is not a directory: {cwd}")
    return resolved


def resolve_instruction_directories(
    root: Path, directories: Sequence[str | Path]
) -> tuple[Path, ...]:
    """Resolve explicit additional instruction directories within a repository."""
    resolved_root = root.resolve()
    resolved_directories: list[Path] = []
    seen: set[Path] = set()
    for directory in directories:
        requested = Path(directory)
        candidate = (
            requested if requested.is_absolute() else resolved_root / requested
        )
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(resolved_root)
        except ValueError as exc:
            raise ValueError(
                f"additional instruction directory escapes repository root: {directory}"
            ) from exc
        if not resolved.is_dir():
            raise ValueError(
                f"additional instruction directory is not a directory: {directory}"
            )
        if resolved not in seen:
            seen.add(resolved)
            resolved_directories.append(resolved)
    return tuple(resolved_directories)


def _inspect_target(
    root: Path,
    target: Path,
    *,
    profile: str,
    session_directory: Path,
    instruction_directories: Sequence[Path],
) -> TargetInspection:
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
        standard_locations, modular_locations = _copilot_cli_locations(
            root, session_directory, target_dir
        )
        sources = _copilot_cli_sources(
            root,
            standard_locations,
            modular_locations,
            instruction_directories,
            relative.as_posix(),
        )

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


def _copilot_cli_locations(
    root: Path, session_directory: Path, target_directory: Path
) -> tuple[list[tuple[Path, str]], list[Path]]:
    session_chain = list(_ancestor_directories(root, session_directory))
    target_chain = list(_ancestor_directories(root, target_directory))

    standard: list[tuple[Path, str]] = []
    for directory in session_chain:
        if directory == root:
            role = "repository root"
        elif directory == session_directory:
            role = "session directory"
        else:
            role = "session intermediate directory"
        standard.append((directory, role))

    standard_paths = set(session_chain)
    target_nested = [
        directory for directory in target_chain if directory not in standard_paths
    ]
    standard.extend((directory, "target-nested directory") for directory in target_nested)

    modular = [root]
    if session_directory != root:
        modular.append(session_directory)
    modular.extend(
        directory
        for directory in target_nested
        if directory not in (root, session_directory)
    )
    return standard, modular


def _copilot_cli_sources(
    root: Path,
    standard_locations: Sequence[tuple[Path, str]],
    modular_locations: Sequence[Path],
    instruction_directories: Sequence[Path],
    target: str,
) -> list[InstructionSource]:
    sources: list[InstructionSource] = []
    discovered: set[Path] = set()
    standard_content_sources: dict[str, str] = {}
    for directory, role in standard_locations:
        standard_sources = (
            (
                directory / ".github" / "copilot-instructions.md",
                "copilot-repository",
                True,
            ),
            (directory / "AGENTS.md", "agents-md", True),
            (directory / "CLAUDE.md", "claude-md", True),
            (directory / ".claude" / "CLAUDE.md", "claude-md", True),
            (directory / "GEMINI.md", "gemini-md", False),
        )
        for path, kind, expands_references in standard_sources:
            if not path.is_file():
                continue
            _append_copilot_source(
                root,
                path,
                InstructionSource(
                    _relative(root, path),
                    kind,
                    "applied",
                    f"combined from a Copilot CLI standard location ({role})",
                ),
                sources,
                discovered,
                expand_references=expands_references,
                standard_content_sources=standard_content_sources,
            )

    for directory in modular_locations:
        modular_root = directory / ".github" / "instructions"
        if modular_root.is_dir():
            _append_modular_sources(
                root,
                sorted(modular_root.rglob("*.instructions.md")),
                target,
                sources,
                discovered,
                reason_suffix="",
            )

    for directory in instruction_directories:
        agents_file = directory / "AGENTS.md"
        if agents_file.is_file():
            _append_copilot_source(
                root,
                agents_file,
                InstructionSource(
                    _relative(root, agents_file),
                    "agents-md",
                    "applied",
                    "combined from an explicit additional instruction directory",
                ),
                sources,
                discovered,
                standard_content_sources=standard_content_sources,
            )
        _append_modular_sources(
            root,
            sorted(directory.rglob("*.instructions.md")),
            target,
            sources,
            discovered,
            reason_suffix=" from an explicit additional instruction directory",
        )
    return sources


def _append_modular_sources(
    root: Path,
    paths: Iterable[Path],
    target: str,
    sources: list[InstructionSource],
    discovered: set[Path],
    *,
    reason_suffix: str,
) -> None:
    for path in paths:
        resolved = path.resolve()
        if resolved in discovered:
            continue
        discovered.add(resolved)
        if not _is_contained(root, resolved):
            sources.append(
                InstructionSource(
                    _relative(root, path),
                    "copilot-path",
                    "invalid",
                    "instruction file escapes repository root through a symlink",
                )
            )
            continue
        frontmatter = _read_apply_to_frontmatter(path)
        patterns = frontmatter.patterns
        if frontmatter.error:
            state = "invalid"
            reason = frontmatter.error
        elif any(_matches(target, pattern) for pattern in patterns):
            state = "applied"
            reason = f"applyTo matches {target}{reason_suffix}"
        else:
            state = "ignored"
            reason = f"applyTo does not match {target}{reason_suffix}"
        sources.append(
            InstructionSource(
                _relative(root, path),
                "copilot-path",
                state,
                reason,
                patterns,
            )
        )


def _append_copilot_source(
    root: Path,
    path: Path,
    source: InstructionSource,
    sources: list[InstructionSource],
    discovered: set[Path],
    *,
    expand_references: bool = True,
    standard_content_sources: dict[str, str] | None = None,
) -> None:
    resolved = path.resolve()
    if resolved in discovered:
        return
    discovered.add(resolved)
    if not _is_contained(root, resolved):
        sources.append(
            InstructionSource(
                source.path,
                source.kind,
                "invalid",
                "instruction file escapes repository root through a symlink",
            )
        )
        return

    content, read_error = _read_instruction_text(path)
    if read_error:
        sources.append(
            InstructionSource(
                source.path,
                source.kind,
                "invalid",
                read_error,
            )
        )
        return

    if standard_content_sources is not None:
        content_key = _standard_instruction_content_key(content)
        first_source = standard_content_sources.get(content_key)
        if first_source is None:
            standard_content_sources[content_key] = source.path
        else:
            source = InstructionSource(
                source.path,
                source.kind,
                "duplicate",
                "duplicate normalized content of first discovered source "
                f"{first_source}; relative references are still evaluated",
            )
    sources.append(source)
    if not expand_references:
        return
    _append_references(
        root,
        path,
        content,
        sources,
        discovered,
        active=(resolved,),
        depth=0,
    )


def _read_instruction_text(path: Path) -> tuple[str, str | None]:
    """Read an instruction without exposing platform-specific failure details."""
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeError:
        return "", "instruction file is not valid UTF-8"
    except OSError:
        return "", "instruction file could not be read"


def _standard_instruction_content_key(content: str) -> str:
    """Return conservatively normalized text for eligible standard instructions."""
    return " ".join(line.strip() for line in content.splitlines() if line.strip())


def _append_references(
    root: Path,
    source_path: Path,
    content: str,
    sources: list[InstructionSource],
    discovered: set[Path],
    *,
    active: tuple[Path, ...],
    depth: int,
) -> None:
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("@") or len(stripped) == 1:
            continue
        reference = stripped[1:].strip()
        if not reference:
            continue
        parent = _relative(root, source_path)
        diagnostic = _resolve_reference(root, source_path, reference)
        if isinstance(diagnostic, str):
            sources.append(
                InstructionSource(
                    reference,
                    "copilot-reference",
                    "invalid",
                    f"{diagnostic} (referenced by {parent})",
                )
            )
            continue

        resolved = diagnostic
        relative = _relative(root, resolved)
        if resolved in active:
            chain = " -> ".join(_relative(root, item) for item in (*active, resolved))
            sources.append(
                InstructionSource(
                    relative,
                    "copilot-reference",
                    "invalid",
                    f"reference cycle: {chain}",
                )
            )
            continue
        if depth >= REFERENCE_DEPTH_LIMIT:
            sources.append(
                InstructionSource(
                    relative,
                    "copilot-reference",
                    "invalid",
                    "reference depth exceeds AgentScope limit of "
                    f"{REFERENCE_DEPTH_LIMIT} (referenced by {parent})",
                )
            )
            continue
        if resolved in discovered:
            continue

        discovered.add(resolved)
        referenced_content, read_error = _read_instruction_text(resolved)
        if read_error:
            sources.append(
                InstructionSource(
                    relative,
                    "copilot-reference",
                    "invalid",
                    f"{read_error} (referenced by {parent})",
                )
            )
            continue
        sources.append(
            InstructionSource(
                relative,
                "copilot-reference",
                "applied",
                f"referenced by {parent}",
            )
        )
        _append_references(
            root,
            resolved,
            referenced_content,
            sources,
            discovered,
            active=(*active, resolved),
            depth=depth + 1,
        )


def _resolve_reference(root: Path, source_path: Path, reference: str) -> Path | str:
    requested = Path(reference)
    if requested.is_absolute():
        return "absolute reference is not loaded"
    if reference == "~" or reference.startswith("~/"):
        return "home-relative reference is not loaded"

    resolved = (source_path.parent / requested).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        return "reference escapes repository root"
    if not resolved.is_file():
        return "referenced file is missing or not a regular file"
    return resolved


def _read_apply_to_frontmatter(path: Path) -> _ApplyToFrontmatter:
    content, read_error = _read_instruction_text(path)
    if read_error:
        return _ApplyToFrontmatter(error=read_error)
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return _ApplyToFrontmatter(error="frontmatter must start with ---")

    closing_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        ),
        None,
    )
    if closing_index is None:
        return _ApplyToFrontmatter(error="frontmatter closing delimiter is missing")

    frontmatter = lines[1:closing_index]
    declarations: list[tuple[int, str]] = []
    malformed_declaration = False
    for index, line in enumerate(frontmatter):
        stripped = line.strip()
        match = re.fullmatch(r"applyTo\s*:(.*)", stripped)
        if match:
            declarations.append((index, match.group(1).strip()))
        elif re.match(r"applyTo(?:\s|$)", stripped):
            malformed_declaration = True

    if malformed_declaration:
        return _ApplyToFrontmatter(error="applyTo declaration is missing a colon")
    if not declarations:
        return _ApplyToFrontmatter(error="frontmatter is missing applyTo")
    if len(declarations) > 1:
        return _ApplyToFrontmatter(error="frontmatter contains duplicate applyTo keys")

    declaration_index, value = declarations[0]
    if not value:
        following = next(
            (
                line.strip()
                for line in frontmatter[declaration_index + 1 :]
                if line.strip()
            ),
            "",
        )
        if following.startswith("-"):
            return _ApplyToFrontmatter(error="applyTo list values are not supported")
        return _ApplyToFrontmatter(error="applyTo scalar is empty")
    if value.startswith("[") or value.startswith("-"):
        return _ApplyToFrontmatter(error="applyTo list values are not supported")
    if value.startswith("{"):
        return _ApplyToFrontmatter(error="applyTo mapping values are not supported")
    if value in ("|", ">"):
        return _ApplyToFrontmatter(error="multiline applyTo values are not supported")

    if value[0] in "\"'":
        if len(value) < 2 or value[-1] != value[0]:
            return _ApplyToFrontmatter(
                error="applyTo has an unterminated quoted scalar"
            )
        value = value[1:-1]
    elif value[-1] in "\"'":
        return _ApplyToFrontmatter(error="applyTo has an unmatched closing quote")

    if not value:
        return _ApplyToFrontmatter(error="applyTo scalar is empty")
    parts = tuple(part.strip() for part in value.split(","))
    if any(not part for part in parts):
        return _ApplyToFrontmatter(error="applyTo contains an empty glob pattern")
    return _ApplyToFrontmatter(patterns=parts)


def _matches(target: str, pattern: str) -> bool:
    normalized = pattern.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
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


def _is_contained(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True

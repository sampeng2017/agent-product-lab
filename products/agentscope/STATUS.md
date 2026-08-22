# AgentScope status

## Product shape

AgentScope v0.2.1 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence; its `copilot-cli` profile combines supported
ancestor formats and evaluates one-line `applyTo` globs. Human and versioned
JSON output are available, with optional missing-instructions and profile-
divergence exit gates.

## Completed on 2026-08-21

- Added a source-linked `applyTo` compatibility matrix based on GitHub's current
  Copilot CLI examples and made it executable as table-driven tests.
- Fixed character-based prefix stripping that corrupted dot paths and silently
  treated leading `/` patterns as repository-relative.
- Preserved exact `./` convenience normalization and the existing `*`, `**`,
  `?`, anchored path, recursive path, and comma-separated behaviors.
- Added an end-to-end OR-semantics regression for scalar comma-separated
  frontmatter, expanding the suite from 12 to 14 tests.
- Revalidated both JSON schemas, inspection and divergence gates, compilation,
  package metadata, and representative existing and planned paths.

## Known issues

- The Copilot profile models repository inputs only, not user-level instruction
  directories or configuration.
- Path-specific frontmatter supports only a scalar, comma-separated `applyTo`.
- `@` references, `excludeAgent`, YAML lists, and syntax errors are not analyzed.
- GitHub's Copilot CLI documentation does not explicitly demonstrate `?`;
  AgentScope documents its conventional single-character behavior as a product
  contract rather than claiming universal Copilot compatibility.

## Decisions

- Stay read-only and dependency-free for the first useful experience.
- Use named client profiles rather than a misleading universal scope model.
- Allow nonexistent targets so maintainers can inspect guidance before creating
  a planned file; resolved paths still cannot escape the selected repository.
- Define divergence strictly from applied source paths: ignored sources do not
  differ in effective guidance and therefore do not fail the gate.
- Treat a leading dot as a real path character; remove only one exact `./`
  relative marker and do not reinterpret a leading `/`.

## Recommended next step

Add `@` reference resolution for `AGENTS.md`, `CLAUDE.md`, and repository-wide
Copilot instructions, with cycle, depth, and repository-escape diagnostics.

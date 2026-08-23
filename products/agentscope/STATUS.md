# AgentScope status

## Product shape

AgentScope v0.3.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence; its `copilot-cli` profile combines supported
ancestor formats, evaluates one-line `applyTo` globs, and recursively resolves
supported `@` imports. Human and versioned JSON output are available, with
optional missing-instructions and profile-divergence exit gates.

## Completed on 2026-08-22

- Expanded references immediately and recursively from `.github/copilot-
  instructions.md`, `AGENTS.md`, `CLAUDE.md`, and referenced files, resolving
  each relative path from its containing file.
- Reported valid imports as applied `copilot-reference` sources and cycles,
  missing/non-file targets, absolute/home paths, repository escapes, and excess
  depth as ordered `invalid` diagnostics.
- Preserved the documented no-expansion boundary for `GEMINI.md` and modular
  `*.instructions.md` sources, plus existing glob and policy behavior.
- Documented the stable human/schema-v1 representation and AgentScope's
  conservative 10-edge cap separately from Copilot's unpublished numeric guard.
- Expanded the suite from 14 to 20 tests while retaining zero dependencies;
  compilation, human/JSON smoke checks, comparison, metadata, and diff checks
  pass.

## Known issues

- The Copilot profile models repository inputs only, not user-level instruction
  directories or configuration.
- Path-specific frontmatter supports only a scalar, comma-separated `applyTo`.
- `excludeAgent`, YAML lists, and syntax errors are not analyzed.
- Invalid reference edges do not yet have a dedicated CI gate or aggregate
  diagnostic count.
- AgentScope does not reproduce Copilot CLI's unpublished import size guard;
  the local 10-edge depth limit is intentionally product-defined.
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
- Preserve JSON schema v1 for references by using the existing source shape;
  compare applied imports as effective guidance and ignore invalid edges.
- Resolve symlinks before enforcing repository containment, and do not expand
  imports from source formats GitHub excludes.

## Recommended next step

Add an optional invalid-reference exit gate and aggregate diagnostic counts for
human and JSON inspection, leaving informational inspection as the default.

# AgentScope status

## Product shape

AgentScope v0.1.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence; its `copilot-cli` profile combines supported
ancestor formats and evaluates one-line `applyTo` globs. Human and versioned
JSON output are available, with an optional missing-instructions exit gate.

## Completed on 2026-08-20

- Compared three current opportunities and selected instruction-scope debugging.
- Implemented safe repository-relative target resolution and two named profiles.
- Added shadowing, aggregation, path-glob, planned-file, error-contract, JSON,
  and gate coverage in seven automated tests.
- Added a product-local `AGENTS.md` so the CLI can inspect its own instructions.

## Known issues

- The Copilot profile models repository inputs only, not user-level instruction
  directories or configuration.
- Path-specific frontmatter supports only a scalar, comma-separated `applyTo`.
- `@` references, `excludeAgent`, YAML lists, and syntax errors are not analyzed.
- There is no cross-profile comparison or explicit divergence warning yet.

## Decisions

- Stay read-only and dependency-free for the first useful experience.
- Use named client profiles rather than a misleading universal scope model.
- Allow nonexistent targets so maintainers can inspect guidance before creating
  a planned file; resolved paths still cannot escape the selected repository.

## Recommended next step

Add `agentscope compare TARGET...` to show both current profiles side by side
and fail optionally when their applied source sets diverge. Cover the command in
human and JSON output before expanding the supported instruction syntax.

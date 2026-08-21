# AgentScope status

## Product shape

AgentScope v0.2.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence; its `copilot-cli` profile combines supported
ancestor formats and evaluates one-line `applyTo` globs. Human and versioned
JSON output are available, with optional missing-instructions and profile-
divergence exit gates.

## Completed on 2026-08-20

- Compared three current opportunities and selected instruction-scope debugging.
- Implemented safe repository-relative target resolution and two named profiles.
- Added shadowing, aggregation, path-glob, planned-file, error-contract, JSON,
  and gate coverage in seven automated tests.
- Added a product-local `AGENTS.md` so the CLI can inspect its own instructions.
- Added a stable comparison model and `agentscope compare` human/JSON surfaces.
- Comparison exposes common and per-profile unique applied paths for one or
  many targets, while unmatched path-specific rules do not create divergence.
- Added `--fail-on-divergence` for CI use and expanded the suite from 7 to 12
  tests across nested sources, proprietary formats, unmatched rules, multiple
  targets, empty guidance, output contracts, and gate behavior.

## Known issues

- The Copilot profile models repository inputs only, not user-level instruction
  directories or configuration.
- Path-specific frontmatter supports only a scalar, comma-separated `applyTo`.
- `@` references, `excludeAgent`, YAML lists, and syntax errors are not analyzed.
- Path matching is a conservative in-house subset and does not yet have a
  compatibility matrix against GitHub's documented glob examples.

## Decisions

- Stay read-only and dependency-free for the first useful experience.
- Use named client profiles rather than a misleading universal scope model.
- Allow nonexistent targets so maintainers can inspect guidance before creating
  a planned file; resolved paths still cannot escape the selected repository.
- Define divergence strictly from applied source paths: ignored sources do not
  differ in effective guidance and therefore do not fail the gate.

## Recommended next step

Build a source-grounded `applyTo` compatibility matrix, then align glob matching
with GitHub's documented path semantics without broadening YAML frontmatter in
the same change.

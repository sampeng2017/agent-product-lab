# AgentScope status

## Product shape

AgentScope v1.0.0 is a frozen, zero-runtime-dependency Python CLI for explaining
which instruction files apply to repository targets. It models explicit
`agents-md` and `copilot-cli` profiles, recursive imports, conservative modular
frontmatter/globs, invalid and non-applied evidence, profile comparison, and a
source-oriented coverage view. Inspection/comparison use schema v5; coverage
uses schema v1.

## Completed on 2026-09-11

- Audited source, tests, help, documentation, metadata, wheel contents, and a
  clean isolated installation across every command surface.
- Added a realistic release fixture with shared, profile-only, matching,
  ignored, and malformed instruction evidence.
- Extended portfolio validation to run installed human inspection, comparison,
  and coverage plus JSON policy cases with exact exit/status assertions.
- Verified schema versions and representative aggregate counts from the wheel.
- Promoted the mature v0.20.0 behavior to v1.0.0 and froze the local MVP.

## Changes since the prior run

No discovery, rendering, public API, gate, or schema behavior changed. The
release boundary is stronger: CI now verifies the built artifact's meaningful
user workflows rather than only importing tests from source and checking the
installed version command.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside additional
  directories remain out of scope.
- GitHub does not document additional-directory precedence or nested `AGENTS.md`
  scope; AgentScope's deterministic behavior stays explicit.
- Content normalization is conservative and not Markdown-semantic.
- Frontmatter supports scalar comma-separated `applyTo` only; `excludeAgent`,
  general YAML, character classes, brace expansion, and negation are not modeled.
- The 10-edge import limit is a product boundary, not a claim about Copilot.
- Hosted portfolio CI is Ubuntu-only, and the repository has no publishing
  remote configured.

## Decisions

- Freeze AgentScope at v1.0.0.
- Preserve inspection/comparison schema v5 and coverage schema v1.
- Keep the product read-only, dependency-free, repository-contained, and
  source-grounded.
- Resume work only for a reproducible defect or documented upstream behavior
  change; do not add speculative filters.

## Validation

- Warning-strict Python 3.11 validation passes all 48 focused tests.
- The portfolio validator compiles sources, builds and isolated-installs the
  v1.0.0 wheel, and runs its console entry point without checkout imports.
- Installed human command paths pass for inspection, comparison, and coverage.
- Installed JSON policy cases return exit 1 and validate schema-v5 inspection,
  schema-v5 comparison, schema-v1 coverage, and representative counts.

## Recommended next step

Leave AgentScope frozen while the portfolio prototypes the selected installed-
artifact behavior contract runner. Reopen only for a concrete regression.

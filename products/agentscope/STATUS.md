# AgentScope status

## Product shape

AgentScope v0.20.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to repository targets. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile models explicit
repository, session, target-nested, and additional-directory discovery,
including modular globs, recursive imports, invalid guidance, and conservative
deduplication. Human and schema-v5 JSON inspection/comparison provide narrow
policy gates. Independent schema-v1 coverage transposes Copilot modular rules
across targets, with detailed and compact human presentations plus display-only
source-path and occurrence-state filtering.

## Completed on 2026-09-10

- Tested mixed matched, ignored, invalid, and not-discovered coverage evidence.
- Added repeatable `coverage --state` selectors for those four outcomes in both
  detailed and compact human reports.
- Selected a mixed-state source when any outcome matches while preserving all
  its occurrences, detailed reasons, compact cells, and discovery order.
- Composed repeated states with OR and state/path filter families with AND.
- Kept complete counts and policy gates, rejected state filters with JSON, and
  preserved the public API plus every existing schema.
- Bumped AgentScope to v0.20.0; the suite now has 48 tests.

## Changes since the prior run

Dense coverage reports can now focus directly on diagnostic outcomes instead of
requiring path knowledge. State filtering remains presentation-only and can be
combined with v0.19.0 source globs without changing enforcement or evidence.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional-directory source shapes but not precedence or
  nested `AGENTS.md` scope; the deterministic AgentScope order is explicit.
- Content normalization is deliberately conservative and not Markdown-semantic.
- Frontmatter supports scalar comma-separated `applyTo` only; `excludeAgent`,
  lists, mappings, multiline values, character classes, brace expansion, and
  glob negation are not modeled.
- The product-defined 10-edge import limit is not Copilot's unpublished size or
  depth guard.
- Hosted portfolio CI is Ubuntu-only.

## Decisions

- Stay read-only and dependency-free.
- Use named profiles and source-grounded compatibility boundaries.
- Keep explicit session/additional-directory state repository-contained and
  deterministic.
- Keep coverage restricted to `copilot-path` sources and distinguish missing
  discovery from an ignored glob.
- Preserve inspection/comparison schema v5 and coverage schema v1.
- Keep compact rendering and all filters presentation-only; JSON, totals, and
  policy evaluation always use complete evidence.
- Repeated values use OR within source or state filters; source and state filter
  families compose with AND, and selected sources retain all occurrences.
- Do not add more filters absent a demonstrated problem.

## Validation

- Warning-strict Python 3.11 portfolio validation passed all 48 AgentScope and
  53 frozen ProofRun tests with one expected optional skip.
- AgentScope 0.20.0 and ProofRun 1.8.1 wheels built, isolated-installed, and
  passed console smokes; temporary output was removed.
- Focused tests, compilation, help inspection, and whitespace checks pass.
- Post-commit ProofRun receipt #68 is valid, and named `unit` evidence applies.

## Recommended next step

Audit the v0.20.0 installed wheel, CLI help, documentation links, and all command
surfaces for release readiness; freeze the MVP if no meaningful defect remains.

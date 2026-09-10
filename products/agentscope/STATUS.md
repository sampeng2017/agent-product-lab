# AgentScope status

## Product shape

AgentScope v0.19.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to repository targets. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile models explicit
repository, session, target-nested, and additional-directory discovery,
including modular globs, recursive imports, invalid guidance, and conservative
deduplication. Human and schema-v5 JSON inspection/comparison provide narrow
policy gates. Independent schema-v1 coverage transposes Copilot modular rules
across targets, with detailed and compact human presentations plus display-only
source-path filtering.

## Completed on 2026-09-09

- Built a 14-source coverage fixture with API/docs rule families, malformed
  guidance, mixed match/ignore states, and target-nested discovery.
- Added repeatable `coverage --source PATH-GLOB` selectors to both detailed and
  compact human reports, preserving first-discovery order.
- Kept the header's complete counts and made displayed-versus-total scope plus
  full-result gate behavior explicit in filtered output.
- Rejected `--source` with JSON, preserving schema-v1 completeness, and proved
  that a filtered-out invalid source still fails its requested policy gate.
- Bumped AgentScope to v0.19.0; the suite now has 47 tests.

## Changes since the prior run

Dense human coverage reports can now be narrowed by subsystem without narrowing
evidence or enforcement. Repeated filters use existing path-glob semantics and
OR composition; filtered detailed and compact views retain source and target
ordering. Inspection, comparison, the public API, and JSON remain unchanged.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional-directory source shapes but not precedence or
  nested `AGENTS.md` scope; the deterministic AgentScope order is explicit.
- Coverage has no occurrence-state display selector for showing only sources
  with ignored or invalid outcomes.
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
- Keep compact rendering presentation-only, use 12-column deterministic chunks,
  retain global caller-order numbering, and keep full legends outside chunks.
- Keep source filtering human-only and display-only; JSON, totals, and policy
  evaluation always use complete evidence.
- Future display filters must state displayed versus complete scope and must not
  narrow policy evaluation.

## Validation

- Warning-strict Python 3.11 portfolio validation passed all 47 AgentScope and
  53 frozen ProofRun tests with one expected optional skip.
- AgentScope 0.19.0 and ProofRun 1.8.1 wheels built, isolated-installed, and
  passed console smokes; temporary output was removed.
- Focused source-filter, compile, help, and whitespace checks passed.

## Recommended next step

Evaluate a display-only occurrence-state selector for quickly isolating ignored
or invalid rules; keep aggregate counts and gates over complete evidence.

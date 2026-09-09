# AgentScope status

## Product shape

AgentScope v0.18.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to repository targets. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile models explicit
repository, session, target-nested, and additional-directory discovery,
including modular globs, recursive imports, invalid guidance, and conservative
deduplication. Human and schema-v5 JSON inspection/comparison provide narrow
policy gates. Independent schema-v1 coverage transposes Copilot modular rules
across targets, with detailed and compact human presentations.

## Completed on 2026-09-08

- Simulated a realistic high-cardinality compact review with 25 targets and
  confirmed the former matrix exceeded 130 columns.
- Added deterministic chunks of at most 12 target columns. Each chunk names its
  global caller-order range and repeats every rule row for direct comparison.
- Kept one ordered full-path rule legend and one ordered target legend, plus the
  default detailed view for occurrence reasons.
- Preserved the prior one-table presentation through 12 targets and left the
  public API, coverage schema v1, aggregate counts, ordering, and gates intact.
- Bumped AgentScope to v0.18.0; the 46-test suite now exercises 25-target
  chunking and bounds rendered row width.

## Changes since the prior run

The compact view is now width-bounded for practical multi-target reviews. A
25-target report renders three labeled chunks and preserves every global target
number, source state, full path, and policy outcome. Inspection and comparison
remain unchanged.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional-directory source shapes but not precedence or
  nested `AGENTS.md` scope; the deterministic AgentScope order is explicit.
- Compact coverage has no source/path filtering. Any filter needs explicit
  display-only semantics so ignored/invalid gates cannot hide failures.
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
- Future display filters must not narrow policy evaluation.

## Validation

- Warning-strict Python 3.11 portfolio validation passed all 46 AgentScope and
  53 frozen ProofRun tests with one expected optional skip.
- AgentScope 0.18.0 and ProofRun 1.8.1 wheels built, isolated-installed, and
  passed console smokes; temporary output was removed.
- Focused chunking, compile, and whitespace checks passed.

## Recommended next step

Test a display-only modular-source filter on a source-dense fixture and retain
complete-result policy gates; do not add target filtering because callers
already select targets explicitly.

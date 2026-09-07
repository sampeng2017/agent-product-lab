# AgentScope status

## Product shape

AgentScope v0.16.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile uses explicit,
repository-contained session and additional-directory inputs to discover
standard and modular instructions, diagnose malformed sources and references,
and explain resolved-path and normalized-content deduplication. Human and
schema-v5 JSON output support missing-instructions, ignored-source,
invalid-reference, invalid-source, and profile-divergence gates. Comparison
preserves ordered per-profile applied, non-applied, and invalid evidence while
keeping policy and divergence semantics distinct from explanatory source states.
Its Copilot-specific coverage command transposes modular rules across requested
targets in independent schema-v1 human and JSON reports.

## Completed on 2026-09-06

- Added `agentscope coverage` and the public `cover_targets` API to group each
  discovered `copilot-path` source's target outcomes.
- Preserved first-discovery source order and caller target order, translating
  applied modular evidence to the clearer coverage state `matched`.
- Added discovered-target counts so a target outside a nested rule's discovery
  route is absent instead of reported as a glob miss.
- Added coverage schema v1 with ordered requested targets, aggregate occurrence
  counts, patterns, reasons, and per-source target occurrences.
- Added modular-only ignored and invalid gates that render full output before
  exit 1; invalid repository input remains exit 2.
- Added two end-to-end regressions and expanded the suite from 43 to 45 tests.

## Changes since the prior run

Callers can now inspect a modular rule once and see its coverage across a target
set, avoiding repeated target-oriented evidence while retaining the exact
discovery and glob semantics. Inspection and comparison schemas and policies
remain unchanged. ProofRun remains frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional directory source shapes but not precedence or
  nested `AGENTS.md` scope; AgentScope's direct-file and post-repository order is
  an explicit deterministic product contract.
- Coverage is source-oriented but uses a vertical occurrence list; very large
  rule/target sets may need an optional compact table or source/path filter.
- Content normalization deliberately ignores line placement, blank lines, and
  surrounding line whitespace only; it does not attempt Markdown semantics.
- A target above the session directory does not reclassify session-intermediate
  directories as target-nested modular locations.
- The frontmatter parser supports only a scalar, comma-separated `applyTo` and
  does not interpret `excludeAgent`, lists, mappings, or multiline values.
- Character classes, brace expansion, and glob negation are not modeled.
- AgentScope does not reproduce Copilot CLI's unpublished import size guard;
  the local 10-edge depth limit is intentionally product-defined.
- GitHub's Copilot CLI documentation does not explicitly demonstrate `?`;
  AgentScope documents conventional single-character behavior as its contract.
- Root hosted CI runs on Ubuntu only; Windows and macOS are not separate matrix
  dimensions.

## Decisions

- Stay read-only and dependency-free for the first useful experience.
- Use named client profiles rather than a misleading universal scope model.
- Keep session and additional-directory state explicit, repository-contained,
  deduplicated, and independent of process environment state.
- Model only a direct `AGENTS.md` plus recursive `*.instructions.md` beneath an
  additional directory; do not infer undocumented nested-agent scope.
- Report repository/session discovery first, then additional directories in
  caller order, without claiming client precedence.
- Deduplicate resolved paths first; compare normalized complete text among
  eligible standard and additional `AGENTS.md` sources, retaining the first.
- Reject any discovered instruction symlink that escapes the selected root.
- Require readable UTF-8 before applying a Copilot source; use stable diagnostic
  categories and never expose file content or platform exception details.
- Preserve `ignored`, `duplicate`, and `shadowed` evidence separately from
  invalid evidence; neither category changes applied-path divergence.
- Let `--fail-on-ignored-sources` enforce only `ignored` evidence; duplicates
  and shadows remain informational unless a future explicit policy says otherwise.
- Keep coverage specific to `copilot-path` sources. Standard instructions,
  references, duplicates, and `agents-md` shadows remain in inspection or
  comparison rather than the modular matrix.
- Treat non-discovery as distinct from an ignored glob outcome and version
  coverage independently at schema v1.
- Treat comparison guidance as present when at least one profile applies a
  source; reserve `--fail-on-divergence` for cross-profile parity enforcement.
- Keep schema v5 for inspection and comparison while versioning the distinct
  source-oriented coverage contract independently.
- Keep portfolio validation in one root script, cover Python 3.10-3.14, promote
  warnings to errors on 3.10, and install wheels only in temporary environments.

## Recommended next step

Dogfood coverage on a larger rule/target set, then decide whether an optional
compact table or source/path filters materially improve diagnosis.

# AgentScope status

## Product shape

AgentScope v0.15.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile uses explicit,
repository-contained session and additional-directory inputs to discover
standard and modular instructions, diagnose malformed sources and references,
and explain resolved-path and normalized-content deduplication. Human and
schema-v5 JSON output support missing-instructions, ignored-source,
invalid-reference, invalid-source, and profile-divergence gates. Comparison
preserves ordered per-profile applied, non-applied, and invalid evidence while
keeping policy and divergence semantics distinct from explanatory source states.

## Completed on 2026-09-05

- Added `--fail-on-ignored-sources` with identical vocabulary and post-render
  exit-1 behavior in direct inspection and comparison.
- Defined the trigger strictly as source state `ignored`, which represents a
  valid modular `applyTo` rule that does not match a requested target.
- Kept duplicates, shadowed ancestors, invalid sources, missing guidance, and
  divergence independent; existing gates continue to compose with OR semantics.
- Preserved inspection and comparison schema v5 because existing ordered source
  objects already expose the exact triggering state.
- Added ignored-count properties and a multi-target regression covering matched,
  ignored, duplicate, shadowed, and invalid sources.
- Bumped the package to v0.15.0 and expanded the suite from 42 to 43 tests.

## Changes since the prior run

Callers can now turn silently unmatched modular guidance into an enforceable CI
failure without broadening the meaning of invalid guidance or non-applied
evidence. The report remains complete and machine-readable before the process
returns 1. ProofRun remains frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional directory source shapes but not precedence or
  nested `AGENTS.md` scope; AgentScope's direct-file and post-repository order is
  an explicit deterministic product contract.
- Reports remain target-oriented and can repeat the same modular source across
  many targets; there is no compact source-to-target coverage view.
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
- Treat comparison guidance as present when at least one profile applies a
  source; reserve `--fail-on-divergence` for cross-profile parity enforcement.
- Keep schema v5 for inspection and comparison because the new gate consumes
  existing source-state evidence rather than adding serialized fields.
- Keep portfolio validation in one root script, cover Python 3.10-3.14, promote
  warnings to errors on 3.10, and install wheels only in temporary environments.

## Recommended next step

Evaluate a source-oriented coverage view that groups each modular rule's matched
and ignored states across requested targets without changing target-oriented
inspection or comparison schemas.

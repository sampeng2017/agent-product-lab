# AgentScope status

## Product shape

AgentScope v0.17.0 is a zero-runtime-dependency Python CLI for explaining the
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
targets in independent schema-v1 human and JSON reports, with an opt-in compact
matrix for larger source/target sets.

## Completed on 2026-09-07

- Dogfooded the vertical coverage view with mixed root/nested modular rules and
  up to ten targets, confirming repeated lines obscure the cross-target shape.
- Added `coverage --compact`, a numbered rule-by-target matrix with distinct
  matched, ignored, invalid, and not-discovered cells.
- Preserved full paths and patterns in first-discovery order, full target paths
  in caller order, and directed reason-seeking users to the detailed view.
- Made `--compact` and `--json` mutually exclusive while leaving schema v1,
  `cover_targets`, aggregate counts, and all policy exits unchanged.
- Bumped AgentScope to v0.17.0 and expanded the suite from 45 to 46 tests.

## Changes since the prior run

Large human reviews now expose their cross-target pattern in one compact matrix
instead of requiring maintainers to mentally join repeated occurrence blocks.
The detailed view still carries reasons, and machine consumers see the same
schema-v1 shape. Inspection and comparison remain unchanged; ProofRun is frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional directory source shapes but not precedence or
  nested `AGENTS.md` scope; AgentScope's direct-file and post-repository order is
  an explicit deterministic product contract.
- Compact matrices still grow horizontally with target count; real-world use
  should justify any future chunking or filtering rather than adding it now.
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
- Keep compact coverage presentation-only, retain full rule/target legends, and
  preserve the detailed vertical view for reasons.
- Treat comparison guidance as present when at least one profile applies a
  source; reserve `--fail-on-divergence` for cross-profile parity enforcement.
- Keep schema v5 for inspection and comparison while versioning the distinct
  source-oriented coverage contract independently.
- Keep portfolio validation in one root script, cover Python 3.10-3.14, promote
  warnings to errors on 3.10, and install wheels only in temporary environments.

## Recommended next step

Exercise compact coverage on a real repository with many modular rules; add
chunking or filters only if horizontal growth remains a practical obstacle.

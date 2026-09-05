# AgentScope status

## Product shape

AgentScope v0.14.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile uses explicit,
repository-contained session and additional-directory inputs to discover
standard and modular instructions, diagnose malformed sources and references,
and explain resolved-path and normalized-content deduplication. Human and
versioned JSON output support missing-instructions, invalid-reference,
invalid-source, and profile-divergence gates. Comparison preserves ordered
per-profile applied, non-applied, and invalid evidence, while keeping policy and
divergence semantics distinct from explanatory source states.

## Completed on 2026-09-04

- Retained `ignored`, `duplicate`, and `shadowed` source objects in profile
  comparisons, preserving each inspection's deterministic order and reasons.
- Added non-applied source counts to profile, target, and aggregate results.
- Rendered per-profile non-applied sections in human comparison output with
  state, path, kind, and reason.
- Advanced comparison JSON to schema v5; inspection remains schema v5.
- Kept divergence based on applied paths and left all policy gates unchanged.
- Added an end-to-end regression covering modular matches and misses, content
  copies, ancestor shadowing, target ordering, human output, and JSON output.
- Bumped the package to v0.14.0 and expanded the suite from 41 to 42 tests.

## Changes since the prior run

Comparison no longer loses explainable non-applied states. Consumers can now
see why a discovered source was skipped without conflating an ignored rule,
duplicate copy, or shadowed ancestor with invalid guidance or divergence.
ProofRun remains frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional directory source shapes but not precedence or
  nested `AGENTS.md` scope; AgentScope's direct-file and post-repository order is
  an explicit deterministic product contract.
- Non-applied comparison evidence is informational; there is no narrow policy
  gate for unmatched modular guidance.
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
- Treat comparison guidance as present when at least one profile applies a
  source; reserve `--fail-on-divergence` for cross-profile parity enforcement.
- Use schema v5 for inspection and comparison; comparison v5 adds ordered
  non-applied source objects and counts to the existing invalid evidence.
- Keep portfolio validation in one root script, cover Python 3.10-3.14, promote
  warnings to errors on 3.10, and install wheels only in temporary environments.

## Recommended next step

Evaluate a narrow ignored-path policy for inspection and comparison so callers
can reject silently unmatched modular guidance without rejecting intentional
duplicates or ancestor shadowing.

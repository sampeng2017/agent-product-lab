# AgentScope status

## Product shape

AgentScope v0.10.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile uses explicit,
repository-contained session and additional-directory inputs to discover
standard and modular instructions, diagnose malformed sources and references,
and explain resolved-path and normalized-content deduplication. Human and
versioned JSON output support missing-instructions, invalid-reference,
invalid-source, and profile-divergence gates.

## Completed on 2026-08-30

- Required directly discovered Copilot standard sources to be readable UTF-8
  before applying, content-normalizing, or expanding them.
- Added deterministic `instruction file is not valid UTF-8` and `instruction
  file could not be read` diagnostics without leaking exception text.
- Made unreadable referenced files invalid reference diagnostics and stopped
  recursive expansion at the failed edge.
- Integrated both failure categories with invalid counts and existing gates;
  informational mode still renders the full report and exits zero.
- Preserved source shapes and inspection/comparison schemas because `invalid`
  sources and their counts are already published fields.
- Added three test methods covering invalid bytes, portable simulated read
  failure, expansion stopping, human/JSON output, policy, and comparison.

## Changes since the prior run

Unreadable Copilot guidance can no longer appear as applied merely because its
path exists. Valid sources retain their prior order and behavior, while invalid
direct and referenced sources are explicit and enforceable. Comparison schemas
remain unchanged and ProofRun remains frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional directory source shapes but not precedence or
  nested `AGENTS.md` scope; AgentScope's direct-file and post-repository order is
  an explicit deterministic product contract.
- Comparison output discards per-profile invalid-source diagnostics and has no
  invalid-source gate; it still compares applied paths only.
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
- Use inspection schema v5 and comparison schema v3 to record the new effective
  input while preserving target and source objects.
- Keep portfolio validation in one root script, cover Python 3.10-3.14, promote
  warnings to errors on 3.10, and install wheels only in temporary environments.

## Recommended next step

Preserve per-profile invalid-source details in comparison results and add an
opt-in invalid-source gate while retaining existing divergence semantics.

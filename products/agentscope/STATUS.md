# AgentScope status

## Product shape

AgentScope v0.11.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile uses explicit,
repository-contained session and additional-directory inputs to discover
standard and modular instructions, diagnose malformed sources and references,
and explain resolved-path and normalized-content deduplication. Human and
versioned JSON output support missing-instructions, invalid-reference,
invalid-source, and profile-divergence gates. Comparison retains per-profile
invalid evidence without conflating it with applied-path divergence.

## Completed on 2026-09-01

- Extended direct comparison results with each profile's ordered invalid source
  objects plus invalid-source and invalid-reference counts.
- Added target and document aggregates to human and JSON comparison output;
  bumped comparison JSON from schema v3 to v4 while inspection remains v5.
- Added `compare --fail-on-invalid-sources`, which composes with the divergence
  gate and emits the complete report before returning exit 1.
- Kept divergence defined only by profile-specific applied paths, so malformed
  or unreadable guidance remains diagnosable without becoming false divergence.
- Preserved the three-argument `ProfileSourceComparison` constructor by giving
  the new invalid evidence field an empty default.
- Added two test methods plus expanded unreadable-source assertions, growing the
  focused suite from 37 to 39 tests.

## Changes since the prior run

Comparison no longer discards the reason a profile could not apply a source.
Consistent-invalid, divergent-invalid, malformed modular, unreadable standard,
and invalid-reference cases retain ordered evidence and can be enforced in CI.
Applied-path comparison semantics remain unchanged and ProofRun remains frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional directory source shapes but not precedence or
  nested `AGENTS.md` scope; AgentScope's direct-file and post-repository order is
  an explicit deterministic product contract.
- Comparison has only the broad invalid-source gate; it does not yet offer the
  narrower invalid-reference-only policy available during inspection.
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
- Keep comparison divergence based only on applied paths; report invalid
  evidence separately and enforce it with an independent policy gate.
- Use inspection schema v5 and comparison schema v4; comparison v4 adds ordered
  per-profile invalid sources and counts without changing inspection objects.
- Keep portfolio validation in one root script, cover Python 3.10-3.14, promote
  warnings to errors on 3.10, and install wheels only in temporary environments.

## Recommended next step

Add a narrow `compare --fail-on-invalid-references` gate for policy parity with
inspection while keeping the broad invalid-source gate unchanged.

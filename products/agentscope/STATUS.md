# AgentScope status

## Product shape

AgentScope v0.12.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile uses explicit,
repository-contained session and additional-directory inputs to discover
standard and modular instructions, diagnose malformed sources and references,
and explain resolved-path and normalized-content deduplication. Human and
versioned JSON output support missing-instructions, invalid-reference,
invalid-source, and profile-divergence gates. Comparison retains per-profile
invalid evidence without conflating it with applied-path divergence and now
offers both narrow-reference and broad-source policies.

## Completed on 2026-09-02

- Added `compare --fail-on-invalid-references`, using existing comparison
  invalid-reference aggregates without changing schema v4.
- Kept malformed non-reference sources outside the narrow gate while the broad
  `--fail-on-invalid-sources` policy continues to reject them.
- Composed the narrow gate with source and divergence policies using OR
  semantics after rendering complete human or JSON diagnostics.
- Added one multi-target policy regression covering malformed modular guidance,
  broken imports, and combined gates; the suite grew from 39 to 40 tests.
- Warning-strict portfolio validation passed both products' suites, wheel
  builds, isolated installs, and installed CLI smokes on Python 3.11.

## Changes since the prior run

Comparison callers can now reject only broken references instead of accepting
all invalid evidence or rejecting every malformed source. Existing ordered
diagnostics, counts, discovery, applied-path comparison, and schemas remain
unchanged. ProofRun remains frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional directory source shapes but not precedence or
  nested `AGENTS.md` scope; AgentScope's direct-file and post-repository order is
  an explicit deterministic product contract.
- Comparison lacks a missing-guidance gate analogous to inspection's
  `--require-instructions`; cross-profile semantics are not yet defined.
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
  evidence separately and offer narrow-reference plus broad-source policy gates.
- Use inspection schema v5 and comparison schema v4; comparison v4 adds ordered
  per-profile invalid sources and counts without changing inspection objects.
- Keep portfolio validation in one root script, cover Python 3.10-3.14, promote
  warnings to errors on 3.10, and install wheels only in temporary environments.

## Recommended next step

Define missing-guidance semantics for comparison without turning intentional
profile-specific coverage into a redundant divergence failure.

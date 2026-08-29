# AgentScope status

## Product shape

AgentScope v0.9.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile uses explicit,
repository-contained session and additional-directory inputs to discover
standard and modular instructions, diagnose malformed sources and references,
and explain resolved-path and normalized-content deduplication. Human and
versioned JSON output support missing-instructions, invalid-reference,
invalid-source, and profile-divergence gates.

## Completed on 2026-08-28

- Rechecked GitHub's current `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` documentation:
  configured directories add `AGENTS.md` and `*.instructions.md` sources, while
  ordering and nested `AGENTS.md` scope remain unspecified.
- Added repeatable `--instructions-dir` input to inspection and comparison
  without implicitly reading the process environment.
- Required each directory to exist, resolve inside the selected repository, and
  remain contained through symlinks; equivalent directory inputs collapse to
  their first occurrence.
- Added direct `AGENTS.md` and recursively sorted `*.instructions.md` discovery
  after ordinary repository/session sources, preserving caller directory order.
- Integrated additional sources with recursive imports, repository-relative
  glob matching, normalized-content copy detection, resolved-route
  deduplication, invalid-source policy exits, and planned targets.
- Rejected source-file symlinks that escape the repository instead of reading
  them, including ordinary and additional discovery routes.
- Recorded the effective directory list in human output, inspection schema v5,
  and comparison schema v3; target and source object shapes remain unchanged.
- Bumped AgentScope to 0.9.0 and expanded the suite from 31 to 34 tests.

## Changes since the prior run

Maintainers can now reproduce configured Copilot instruction discovery without
hidden environment state. Saved output includes the effective, deduplicated
directory list, and the same policy gates diagnose malformed or escaping
additional sources. ProofRun remains frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional directory source shapes but not precedence or
  nested `AGENTS.md` scope; AgentScope's direct-file and post-repository order is
  an explicit deterministic product contract.
- Unreadable or non-UTF-8 standard files cannot be content-compared and retain
  applied-source behavior; unreadable modular files are invalid.
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
- Use inspection schema v5 and comparison schema v3 to record the new effective
  input while preserving target and source objects.

## Recommended next step

Add a repository-level CI workflow that validates both AgentScope and the
frozen ProofRun product, including Python 3.10/3.11 compatibility and isolated
wheel-install smoke tests from one maintained entry point.

# AgentScope status

## Product shape

AgentScope v0.7.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile uses an explicit
repository-contained session directory to distinguish root, intermediate,
session, and target-nested standard locations; excludes modular instructions
from intermediate-only directories; evaluates scalar `applyTo` globs; diagnoses
malformed frontmatter; recursively resolves supported `@` imports; and
deduplicates resolved files across discovery routes. Human and versioned JSON
output support missing-instructions, invalid-reference, invalid-source, and
profile-divergence gates.

## Completed on 2026-08-26

- Added `--cwd` to inspection and comparison as explicit model state relative
  to `--root`; it defaults to the repository root and never changes the process
  working directory.
- Required the session directory to exist, be a directory, and remain within
  the repository after symlink resolution.
- Added role-aware standard discovery and excluded modular trees from
  session-intermediate-only directories while retaining root, session, and
  target-nested modular discovery.
- Preserved the previous target-ancestor behavior for the default root session,
  including direct/reference deduplication and deterministic order.
- Added coverage for nested sessions, divergent branches, planned targets,
  containment, compatibility, human reasons, and inspection/comparison JSON.
- Added the repository-relative session path to inspection schema v4 and
  comparison schema v2, bumped AgentScope to 0.7.0, and expanded the suite from
  25 to 29 tests.

## Changes since the prior run

The Copilot model now separates a live session's working directory from the
file target instead of treating every target ancestor as equivalent. This
closes the documented modular-instruction exception without adding implicit
environment state.

## Known issues

- User-level locations, `COPILOT_HOME`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, and
  interactive source disabling remain out of scope.
- Deduplication recognizes resolved file identity, not identical content stored
  at different paths.
- A target above the session directory does not reclassify session-intermediate
  directories as target-nested modular locations.
- The frontmatter parser deliberately supports only a scalar, comma-separated
  `applyTo`; it diagnoses rather than interprets YAML lists, mappings, and
  multiline values.
- `excludeAgent` is accepted as an uninterpreted sibling key, and character
  classes, brace expansion, and negation are not modeled.
- AgentScope does not reproduce Copilot CLI's unpublished import size guard;
  the local 10-edge depth limit is intentionally product-defined.
- GitHub's Copilot CLI documentation does not explicitly demonstrate `?`;
  AgentScope documents its conventional single-character behavior as a product
  contract.

## Decisions

- Stay read-only and dependency-free for the first useful experience.
- Use named client profiles rather than a misleading universal scope model.
- Anchor explicit relative session directories at the selected root, require
  an existing contained directory, and use the root as the stable default.
- Search ordinary standard files at root, session intermediates, session, and
  target-only locations; search modular trees at root, session, and target-only
  locations, never intermediate-only directories.
- Present the session branch before a divergent target branch. This is output
  stability, not a precedence claim.
- Deduplicate direct and referenced sources by resolved path; first discovery
  wins.
- Allow nonexistent targets so maintainers can inspect planned files.
- Use inspection schema v4 and comparison schema v2 for the additive session
  context; preserve nested target/source shapes and policy behavior.

## Recommended next step

Add explainable identical-content deduplication for eligible Copilot standard
files while preserving resolved-path deduplication and reference order.

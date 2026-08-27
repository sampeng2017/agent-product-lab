# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains the AgentScope v0.7.0 Python package, 29
  tests, source-linked compatibility contracts, and product documentation.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs.

AgentScope models two explicit profiles. `agents-md` applies the closest
ancestor `AGENTS.md` and explains shadowed files. `copilot-cli` combines
repository standard locations using an explicit repository-contained session
directory, distinguishes session intermediates from target-nested locations,
excludes modular instructions from intermediate-only directories, evaluates
scalar `applyTo` globs, and expands supported recursive `@` imports. Inspection
emits human or schema-v4 JSON with optional policy gates; comparison emits human
or schema-v2 JSON and can gate applied-source divergence.

## Completed today (2026-08-26)

- Rechecked GitHub's current Copilot CLI instruction-location contract and
  confirmed its intermediate-directory exception for modular instructions.
- Added explicit `--cwd` support to inspection and comparison without changing
  the process directory or reading hidden process state. Relative values are
  anchored at `--root`; nonexistent, non-directory, outside, and symlink-escape
  values fail as invalid repository input.
- Classified discovery into repository root, session intermediate, session,
  and target-nested roles. Standard files use all roles; modular trees skip
  intermediate-only locations.
- Preserved v0.6.0 root-to-target behavior when `--cwd .` is used, including
  deterministic ordering and first-resolved-route deduplication.
- Covered nested and divergent session/target paths, planned targets, default
  compatibility, containment, source reasons, and both CLI JSON surfaces.
- Added `session_directory` to inspection schema v4 and comparison schema v2,
  bumped AgentScope to 0.7.0, and expanded the suite from 25 to 29 tests.
- Revalidated the frozen ProofRun baseline without changing its product scope.

## Changes since the prior run

AgentScope moved from treating the entire target-ancestor chain uniformly to a
session-aware Copilot discovery model. It can now explain why ordinary standard
files are found in intermediate directories while modular files there are
excluded. ProofRun remains frozen, and no Sam request is active.

## Known issues

- The Copilot profile models repository inputs only, not user-level locations,
  `COPILOT_HOME`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, or interactive file
  disabling.
- Deduplication is based on resolved file identity, not identical file content.
- A target above the selected session directory is supported conservatively:
  its already-visited session-intermediate directories are not reclassified as
  target-nested modular locations.
- The dependency-free frontmatter parser diagnoses rather than interprets YAML
  lists, mappings, and multiline `applyTo` values; `excludeAgent` is accepted
  but not modeled.
- Character classes, brace expansion, and glob negation are not modeled.
- Copilot documents depth and size guards without publishing numeric limits.
  AgentScope's 10-edge cap is explicitly its own conservative contract, and it
  does not model the client's unpublished size guard.
- Client behavior can evolve, so profile assumptions need source-linked tests
  and explicit versioning as support expands.
- `?` retains conventional one-character behavior, but GitHub's Copilot CLI
  page does not publish an explicit `?` example.
- The repository has no root CI workflow; each product is validated from its
  own directory for now.

## Decisions

- AgentScope, not ProofRun, is the active product for future runs.
- Keep the first experience read-only, credential-free, and dependency-free.
- Model named agent profiles rather than claiming universal compatibility.
- Treat `--cwd` as explicit repository-relative model input, default it to the
  repository root, require an existing contained directory, and never infer it
  from the process working directory.
- Present standard locations in root/intermediate/session/target role order;
  search modular trees at root/session/target locations only. This is stable
  explanation order, not a precedence claim.
- Deduplicate direct and referenced sources by resolved path; first discovery
  wins.
- Keep nonexistent contained targets inspectable so planned files are supported.
- Version the additive session context as inspection schema v4 and comparison
  schema v2 while retaining their existing nested object shapes.

## Recommended next step

Model GitHub's identical-content deduplication for eligible Copilot standard
files with an explainable duplicate state and tests that preserve resolved-path
deduplication and reference ordering.

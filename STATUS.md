# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains the AgentScope v0.8.0 Python package, 31
  tests, source-linked compatibility contracts, and product documentation.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs.

AgentScope models two explicit profiles. `agents-md` applies the closest
ancestor `AGENTS.md` and explains shadowed files. `copilot-cli` combines
repository standard locations using an explicit repository-contained session
directory, evaluates scalar `applyTo` globs, expands supported recursive `@`
imports, diagnoses invalid sources, and explains later standard files whose
normalized complete content duplicates the first discovered copy. Inspection
emits human or schema-v4 JSON with optional policy gates; comparison emits human
or schema-v2 JSON and can gate applied-source divergence.

## Completed today (2026-08-28)

- Rechecked GitHub's current Copilot CLI duplicate-copy contract and confirmed
  that content deduplication applies to repository-wide and agent standard
  instructions, not modular path-specific files.
- Added conservative whole-file normalization across standard kinds and every
  modeled root, intermediate, session, target, and divergent discovery role.
- Kept the first standard source applied and surfaced later distinct paths as
  `duplicate`, with the retained path in both human and JSON reasons.
- Continued resolving relative imports from duplicate wrappers so distinct
  referenced files remain visible; imports do not seed the standard-copy map.
- Preserved resolved-path/symlink deduplication, deterministic ordering, modular
  diagnostics, policy exits, and current JSON schemas.
- Bumped AgentScope to 0.8.0 and expanded its passing suite from 29 to 31 tests.
- Revalidated the frozen ProofRun baseline without changing its product scope.

## Changes since the prior run

AgentScope now models both documented duplicate mechanisms: the same resolved
file is reported once by its first route, while distinct eligible standard files
with the same normalized complete content retain provenance through an explicit
`duplicate` source state. ProofRun remains frozen, and no Sam request is active.

## Known issues

- User-level locations, `COPILOT_HOME`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, and
  interactive file disabling remain out of scope.
- Unreadable or non-UTF-8 standard files cannot be content-compared and retain
  the prior applied-source behavior.
- Content normalization ignores line placement, blank lines, and surrounding
  line whitespace; it deliberately avoids partial or semantic similarity.
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
- Treat explicit session and future discovery inputs as reproducible model
  state; do not infer them from the process environment.
- Present standard locations in stable role order without claiming precedence.
- Deduplicate resolved file identity first, then compare normalized complete
  text only among eligible standard files; the first discovered source wins.
- Report later copies as `duplicate` but evaluate their relative imports from
  their own locations. Exclude modular and imported files from the content map.
- Keep nonexistent contained targets inspectable so planned files are supported.
- Preserve inspection schema v4 and comparison schema v2 because source-object
  shape did not change and comparison still includes applied paths only.

## Recommended next step

Evaluate an explicit, repeatable, repository-contained option for additional
Copilot instruction directories without reading
`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` as hidden process state.

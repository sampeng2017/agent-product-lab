# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains the AgentScope v0.6.0 Python package, tests,
  source-linked compatibility contracts, product documentation, and contributor
  instructions.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs.

AgentScope models two explicit profiles. `agents-md` applies the closest
ancestor `AGENTS.md` and explains shadowed files. `copilot-cli` combines
repository standard locations along the target-ancestor chain, including
nested `.github/copilot-instructions.md`, `.claude/CLAUDE.md`, modular path
instructions, and supported recursive `@` imports. Inspection emits human or
schema-v3 JSON with invalid-source and invalid-reference counts and optional
policy gates. Comparison remains schema v1 and can gate applied-source
divergence.

## Completed today (2026-08-25)

- Rechecked GitHub's current Copilot CLI discovery documentation and captured a
  source-linked repository discovery contract.
- Added `.claude/CLAUDE.md` and nested target-ancestor standard locations for
  repository-wide, agent, and modular path instructions.
- Defined deterministic root-to-target presentation: standard files first in a
  documented per-directory order, followed by sorted modular trees. This is a
  reporting contract, not a Copilot precedence claim.
- Unified direct and referenced discovery around resolved-file identity. The
  first route wins, references remain immediate and depth-first, and later
  direct or equivalent symlink routes do not duplicate a source.
- Kept inspection schema v3, comparison schema v1, recursive-reference
  boundaries, frontmatter diagnostics, source objects, and policy exits stable.
- Bumped AgentScope to 0.6.0 and expanded its suite from 23 to 25 tests.
- Revalidated the frozen ProofRun baseline without changing its product scope.

## Changes since the prior run

AgentScope advanced from root-only Copilot repository and modular discovery to
a documented target-ancestor model that includes `.claude/CLAUDE.md`, nested
standard locations, deterministic ordering, and cross-route deduplication.
ProofRun remains frozen. No Sam request is active.

## Known issues

- AgentScope does not model a separate Copilot session working directory, so it
  cannot yet distinguish intermediate session ancestors from target-nested
  directories when applying modular discovery rules.
- The Copilot profile models repository inputs only, not user-level locations,
  `COPILOT_HOME`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, or interactive file
  disabling.
- Deduplication is based on resolved file identity, not identical file content.
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
- Treat the selected repository root and target-ancestor chain as the explicit
  repository discovery inputs until a separate session-directory option exists.
- Present standard sources root-to-target, expand supported references
  immediately, then present modular sources root-to-target in path order.
- Treat ordering as deterministic explanation only because GitHub defines no
  general precedence among combined sources.
- Deduplicate every direct or referenced source by resolved path and retain its
  first discovery route.
- Permit nonexistent in-repository targets while rejecting absolute or
  symlink-resolved repository escapes.
- Keep inspection schema v3 and comparison schema v1 stable for this additive
  discovery release.

## Recommended next step

Add an explicit repository-contained Copilot session-directory input and model
root, session-intermediate, and target-nested locations separately, especially
the documented exclusion of modular instructions from intermediate-only
directories.

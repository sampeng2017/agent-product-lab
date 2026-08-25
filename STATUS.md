# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains the AgentScope v0.5.0 Python package, tests,
  compatibility contracts, product documentation, and contributor instructions.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs.

AgentScope models two explicit profiles. `agents-md` applies the closest
ancestor `AGENTS.md` and explains shadowed files. `copilot-cli` combines
repository-wide Copilot guidance, ancestor `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`,
matching path-specific files, and supported recursive `@` imports. Inspection
emits human or schema-v3 JSON with aggregate and per-target invalid-source and
invalid-reference counts. Missing guidance, invalid imports, and any invalid
source can be gated independently or together. Comparison remains schema v1 and
can gate applied-source divergence.

## Completed today (2026-08-24)

- Classified malformed path-instruction frontmatter as precise ordered
  `invalid` sources, including missing delimiters or keys, empty scalars, lists,
  mappings, multiline values, duplicate keys, malformed declarations and
  quotes, and empty comma items.
- Preserved valid scalar glob behavior and kept valid nonmatching rules
  `ignored`, so a scope miss is distinguishable from broken configuration.
- Added broader aggregate and per-target `invalid_source_count` values while
  preserving `invalid_reference_count` as a compatible subset.
- Added the opt-in `--fail-on-invalid-sources` policy without changing the
  narrower `--fail-on-invalid-references` contract. All inspection gates retain
  informational defaults, OR composition, and exit 2 for invalid input.
- Versioned inspection JSON to schema v3, documented migration and the
  source-grounded frontmatter boundary, bumped AgentScope to 0.5.0, and expanded
  its suite from 21 to 23 tests.
- Revalidated frozen ProofRun without changing its product scope.

## Changes since the prior run

AgentScope advanced from v0.4.0's reference-only configuration diagnostics to a
v0.5.0 source-health model that can distinguish malformed path rules from valid
glob misses and enforce the distinction in CI. ProofRun remains frozen. No Sam
request is active.

## Known issues

- AgentScope's Copilot model currently covers repository inputs, not user-level
  instruction directories or configuration.
- Repository discovery does not yet cover every documented Copilot CLI location,
  including `.claude/CLAUDE.md` and nested standard-location nuances.
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
  page does not publish an explicit `?` example; the matrix marks this boundary.
- The repository has no root CI workflow; each product is validated from its own
  directory for now.

## Decisions

- AgentScope, not ProofRun, is the active product for future runs.
- Keep the first experience read-only, credential-free, and dependency-free.
- Model named agent profiles rather than claiming universal compatibility.
- Permit nonexistent in-repository targets while rejecting absolute or
  symlink-resolved repository escapes.
- Treat malformed path frontmatter as invalid and a valid glob miss as ignored.
- Keep `--fail-on-invalid-references` narrow; expose the broader superset as
  `--fail-on-invalid-sources` rather than silently changing policy behavior.
- Count invalid diagnostics per target and expose reference counts as a subset,
  because one shared source can affect several actionable assessments.
- Keep source objects and comparison schema v1 stable; version inspection JSON
  to v3 for its additive broader counts.
- Compare only applied paths, resolve imports relative to their containing file,
  and preserve ordered, repository-bound diagnostics.

## Recommended next step

Audit and implement remaining repository-scoped Copilot CLI discovery locations,
beginning with `.claude/CLAUDE.md`, with source-linked ordering and deduplication
tests before considering user-level instructions.

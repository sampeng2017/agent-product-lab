# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains the AgentScope v0.4.0 Python package, tests,
  opportunity evidence, product documentation, and contributor instructions.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs.

AgentScope models two explicit profiles. `agents-md` applies the closest
ancestor `AGENTS.md` and explains shadowed files. `copilot-cli` combines
repository-wide Copilot guidance, ancestor `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`,
matching path-specific files, and supported recursive `@` imports. Inspection
emits human or schema-v2 JSON with aggregate and per-target invalid-reference
counts. Missing guidance and invalid imports can be gated independently or
together. Comparison remains schema v1 and can gate applied-source divergence.

## Completed today (2026-08-23)

- Added the opt-in `--fail-on-invalid-references` inspection policy while
  retaining an informational exit 0 default and exit 2 for invalid input.
- Defined OR composition with `--require-instructions` across multiple targets;
  the complete human or JSON report is emitted before a policy exit 1.
- Added aggregate and per-target invalid-reference counts to human output and
  inspection JSON while preserving every ordered source-level reason.
- Versioned inspection JSON to schema v2 and documented its additive migration;
  the unchanged comparison JSON contract remains schema v1.
- Bumped AgentScope to 0.4.0 and expanded its suite from 20 to 21 tests.
- Revalidated frozen ProofRun without changing its product scope.

## Changes since the prior run

AgentScope advanced from v0.3.0's informational reference diagnostics to a
CI-enforceable v0.4.0 policy and countable output contract. ProofRun remains
frozen. No Sam request is active.

## Known issues

- AgentScope's Copilot model currently covers repository inputs, not user-level
  instruction directories.
- Path-specific frontmatter accepts a scalar `applyTo` only; malformed or
  unsupported forms are reported as ignored rather than as precise diagnostics.
- `excludeAgent`, YAML lists, and syntax errors are not modeled.
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
- Permit nonexistent in-repository targets so users can inspect planned files,
  while rejecting absolute or symlink-resolved repository escapes.
- Keep the executable compatibility matrix synchronized with every matcher
  change and avoid silently normalizing undocumented absolute-style patterns.
- Treat only differences in applied paths as divergence; ignored and invalid
  discovery results remain useful but do not trip comparison policy.
- Resolve imports relative to their containing file, keep them repository-bound,
  expand only from documented file types, and retain ordered invalid reasons.
- Count invalid references per target, compose inspection gates with OR
  semantics, and reserve exit 2 for invalid repository arguments.
- Version inspection JSON to v2 for additive diagnostic counts while keeping
  the structurally unchanged comparison schema at v1.

## Recommended next step

Turn malformed path-instruction frontmatter into explicit diagnostics, cover
unsupported YAML lists and delimiters, and evaluate a broader invalid-source
gate without weakening the existing reference-specific contract.

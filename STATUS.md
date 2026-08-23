# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains the AgentScope v0.3.0 Python package, tests,
  opportunity evidence, product documentation, and contributor instructions.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs.

AgentScope currently models two explicit profiles. `agents-md` applies the
closest ancestor `AGENTS.md` and explains shadowed files. `copilot-cli` combines
repository-wide Copilot guidance, ancestor `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`,
and matching path-specific instruction files. It emits human or versioned JSON
output and can fail when a target has no applied guidance. Supported Copilot
`@` imports are resolved recursively, while invalid edges are explained without
being counted as applied. Comparison shows common and profile-only applied
sources and can fail on divergence.

## Completed today (2026-08-22)

- Added depth-first `@path` resolution for repository Copilot instructions,
  `AGENTS.md`, `CLAUDE.md`, and recursively referenced files.
- Added explicit diagnostics for cycles, missing/non-file targets, absolute and
  home-relative paths, repository and symlink escapes, and a documented 10-edge
  AgentScope safety limit.
- Preserved GitHub's boundary: imports are not expanded from `GEMINI.md` or
  `*.instructions.md`; repeated referenced files are reported once.
- Kept schema-v1 JSON structurally stable by using the existing source object
  with the new `copilot-reference` kind and `invalid` state. Applied imports
  participate in profile comparison; invalid edges do not.
- Added a source-linked reference contract and six end-to-end tests, expanding
  AgentScope from 14 to 20 tests with no runtime dependency.
- Revalidated frozen ProofRun: 53 tests passed with one expected optional
  pytest-runtime skip, and its receipt chain remains audit-valid.

## Changes since the prior run

AgentScope advanced from v0.2.1 to v0.3.0 with explainable recursive Copilot
instruction imports. ProofRun remains frozen. No Sam request is active.

## Known issues

- AgentScope's Copilot model currently covers repository inputs, not user-level
  instruction directories.
- Path-specific frontmatter accepts a scalar `applyTo` only; YAML lists,
  `excludeAgent`, and syntax errors are not modeled.
- Reference diagnostics are informational; there is no dedicated nonzero gate
  or aggregate diagnostic count yet.
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
- Treat only differences in applied paths as divergence; ignored discovery
  results remain useful in inspection mode but do not trip comparison policy.
- Resolve imports relative to their containing file, keep them repository-bound,
  expand only from documented file types, and represent invalid edges without
  changing the schema-v1 source-object shape.

## Recommended next step

Add `--fail-on-invalid-references` plus aggregate invalid-reference counts in
human and JSON inspection output, retaining informational behavior by default.

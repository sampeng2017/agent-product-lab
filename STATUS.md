# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains the AgentScope v0.2.1 Python package, tests,
  opportunity evidence, product documentation, and contributor instructions.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs.

AgentScope currently models two explicit profiles. `agents-md` applies the
closest ancestor `AGENTS.md` and explains shadowed files. `copilot-cli` combines
repository-wide Copilot guidance, ancestor `AGENTS.md`/`CLAUDE.md`/`GEMINI.md`,
and matching path-specific instruction files. It emits human or versioned JSON
output and can fail when a target has no applied guidance. Its comparison mode
shows common and profile-only applied sources and can fail on divergence.

## Completed today (2026-08-21)

- Captured GitHub's current Copilot CLI glob examples in a source-linked,
  executable compatibility matrix covering root anchoring, nested paths, `*`,
  `**`, `?`, dot paths, explicit relative prefixes, and comma-separated rules.
- Fixed leading-dot corruption in matcher normalization: `.github/**` and `.*`
  now preserve their dots, while undocumented leading `/` patterns are no
  longer silently changed into repository-relative matches.
- Added table-driven matcher coverage plus an end-to-end scalar frontmatter OR
  test, expanding AgentScope from 12 to 14 tests without a runtime dependency.
- Preserved both schema-v1 JSON surfaces and policy-gate behavior.
- Revalidated frozen ProofRun: 53 tests passed with one expected optional
  pytest-runtime skip, and all 49 receipts remain audit-valid.

## Changes since the prior run

AgentScope advanced from v0.2.0 to v0.2.1 with a documented matching contract
and correct dot-path behavior. ProofRun remains frozen. No Sam request is active.

## Known issues

- AgentScope's Copilot model currently covers repository inputs, not user-level
  instruction directories.
- Path-specific frontmatter accepts a scalar `applyTo` only; YAML lists,
  `excludeAgent`, and `@` references are not modeled.
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

## Recommended next step

Add `@` reference resolution for supported Copilot CLI instruction files, with
cycle, depth, and repository-escape detection plus explicit diagnostic output.

# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains the AgentScope v0.2.0 Python package, tests,
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

## Completed today

- Inspected Git state/history, automation memory, all portfolio and handoff
  documentation, ProofRun implementation/tests, and active `To-Sam/` messages.
- Revalidated the frozen ProofRun baseline: 53 tests passed with one expected
  optional pytest-runtime skip.
- Researched and compared instruction scoping, MCP configuration review, and
  coding-agent environment preflight using current official documentation and
  visible open-source alternatives.
- Selected AgentScope, replaced the temporary product placeholder, and built a
  runnable zero-runtime-dependency v0.1.0 prototype with seven passing tests.
- Added exact run instructions, known limits, product promise, success signal,
  and a source-linked opportunity record.
- Implemented the planned cross-profile comparison as a separate immutable data
  model plus human and schema-v1 JSON output.
- Added a divergence gate and five tests covering nested/proprietary sources,
  unmatched rules, multiple targets, empty guidance, and CLI contracts.

## Changes since the prior run

AgentScope advanced from a single-profile-at-a-time v0.1.0 prototype to a v0.2.0
comparison workflow suitable for local inspection and CI policy. ProofRun was
left frozen. No Sam request is active.

## Known issues

- AgentScope's Copilot model currently covers repository inputs, not user-level
  instruction directories.
- Path-specific frontmatter accepts a scalar `applyTo` only; YAML lists,
  `excludeAgent`, and `@` references are not modeled.
- Client behavior can evolve, so profile assumptions need source-linked tests
  and explicit versioning as support expands.
- The current `applyTo` matcher is deliberately narrow and needs a documented
  compatibility matrix before broader syntax support.
- The repository has no root CI workflow; each product is validated from its own
  directory for now.

## Decisions

- AgentScope, not ProofRun, is the active product for future runs.
- Keep the first experience read-only, credential-free, and dependency-free.
- Model named agent profiles rather than claiming universal compatibility.
- Permit nonexistent in-repository targets so users can inspect planned files,
  while rejecting absolute or symlink-resolved repository escapes.
- Prefer cross-profile divergence visibility before adding more syntax breadth.
- Treat only differences in applied paths as divergence; ignored discovery
  results remain useful in inspection mode but do not trip comparison policy.

## Recommended next step

Align `applyTo` glob matching with GitHub's documented semantics using a focused
compatibility matrix, retaining dependency-free operation and both existing
JSON contracts. Then consider `@` reference resolution with cycle detection.

# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains AgentScope v0.18.0, 46 tests, source-linked
  compatibility contracts, and product documentation.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs. A
  read-only portfolio CI workflow validates both products on Python 3.10-3.14.

AgentScope models explicit `agents-md` and `copilot-cli` profiles. Inspection
and comparison emit human or schema-v5 JSON, preserve applied, non-applied, and
invalid evidence, and provide narrow policy gates. Independent schema-v1
coverage groups Copilot modular rules across targets; its compact human matrix
now chunks high-cardinality target sets without changing underlying evidence.

## Completed today (2026-09-08)

- Revalidated the clean v0.17.0 baseline and found no active Sam message.
- Exercised compact coverage with 25 ordered targets, demonstrating that the
  former single table exceeded 130 columns and grew without a bound.
- Added deterministic 12-target column chunks with labeled global ranges,
  repeated rule rows, and one complete ordered rule/target legend.
- Preserved the existing layout for at most 12 targets, schema-v1 JSON, public
  coverage results, target/source ordering, detailed output, and policy exits.
- Bumped AgentScope to v0.18.0; the focused suite remains 46 tests with expanded
  high-cardinality coverage.

## Changes since the prior run

Compact coverage no longer becomes arbitrarily wide as more targets are
requested. A 25-target report now renders three tables whose rule rows stay at
65 characters or fewer, while numbered legends still expose every full path.
No inspection, comparison, discovery, JSON, or gate contract changed.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, nested
  `AGENTS.md` interpretation inside additional directories, and interactive
  file disabling remain out of scope.
- GitHub does not document precedence or nested `AGENTS.md` scope for configured
  directories; AgentScope's direct-file and post-repository order is explicit.
- Compact coverage has no source filter; adding one requires a clear decision
  that policy gates still evaluate the complete unfiltered evidence set.
- Content normalization ignores line placement, blank lines, and surrounding
  line whitespace but deliberately avoids semantic similarity.
- The dependency-free frontmatter parser supports only scalar `applyTo` values;
  lists, mappings, multiline values, and `excludeAgent` behavior are not modeled.
- Character classes, brace expansion, glob negation, the client's unpublished
  import size limit, and interactive source disabling are not modeled.
- Client behavior can evolve, so profile assumptions require source-linked tests
  and explicit schema/version changes.
- Root CI currently runs on Ubuntu only; Windows/macOS behavior remains covered
  by portable implementation design and focused platform code, not hosted jobs.

## Decisions

- AgentScope, not ProofRun, is the active product for future runs.
- Keep the first experience read-only, credential-free, dependency-free, and
  explicit about the modeled client profile.
- Keep session and additional-directory state reproducible and contained by the
  selected repository; do not infer it from the process environment.
- Preserve planned targets and keep applied, non-applied, and invalid evidence
  distinct in inspection and comparison schema v5.
- Keep modular coverage Copilot-specific and version it independently at schema
  v1; exclude standards, references, copies, and shadows from this view.
- Treat not-discovered targets separately from ignored glob outcomes.
- Keep compact coverage presentation-only. Chunk after 12 targets using global
  caller-order numbers and retain one complete legend plus the detailed view.
- Any future presentation filter must not silently narrow gate evaluation.
- Keep portfolio validation in one root script across Python 3.10-3.14 and
  install wheels only in temporary environments.

## Validation

- Warning-strict Python 3.11 portfolio validation passed 46 AgentScope tests and
  53 ProofRun tests with one expected optional skip.
- Both wheels built, installed in isolated temporary environments, and passed
  console smokes; AgentScope reported version 0.18.0.
- The default Python 3.14 interpreter still lacks the declared local
  `setuptools>=68` build backend, and the validator correctly fails preflight.

## Recommended next step

Evaluate whether a presentation-only modular-source filter materially improves
large reports. If implemented, keep policy gates over the complete result set
and clearly disclose that filtering changes display only.

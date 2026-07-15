# ProofRun status

## Current product idea

ProofRun is a local-first CLI that records verification receipts for existing
development commands and binds them to the exact Git working state they covered.

## Current product shape

The dependency-free Python CLI has six commands: `run`, `verify`, `status`,
`audit`, `report`, and `history`. Receipts stay in append-only JSON Lines under
the ignored `.proofrun/` directory. Manifest checks can run from distinct
repository subdirectories with explicit environment overrides, sequentially or
with bounded `--jobs N` concurrency. Parallel suites report results in manifest
order and append receipts in completion order. Schema-v4 receipts preserve the
execution context alongside Git snapshots, file-level drift details, canonical
SHA-256 hashes, and links to prior receipts. A repository-local OS lock
serializes the load-link-append critical section so concurrent writers preserve
one ordered chain without serializing command execution; readers coordinate
with the lock for consistent snapshots. Status explains whether evidence still
applies, audit detects local receipt-chain damage, and report packages both
views into a Markdown handoff.
Human status and reports cap invalidating paths at 10 by default with explicit
overflow counts; structured JSON remains complete.

## Completed today

- Added `proofrun verify --jobs N` with a strict positive worker count and a
  sequential default for backward compatibility.
- Implemented bounded scheduling with deterministic manifest-order results,
  while the existing store lock safely records receipts in completion order.
- Defined parallel fail-fast behavior: stop launching checks after observing a
  failure, let already-running checks finish, and preserve all their receipts.
- Added concurrency, fail-fast, invalid-worker-count, and CLI-wiring
  regressions; expanded the suite to 25 tests.
- Bumped the package to version 0.8.0 and documented parallel execution and
  ordering semantics.

## Changed since the previous run

Manifest suites can now use multiple cores without starting an unbounded number
of child processes or sacrificing receipt integrity. Existing invocations still
run one check at a time, and parallel completion timing no longer makes the
human summary order nondeterministic.

## Known issues and incomplete work

- Hash chaining is tamper-evident, not authenticated: someone able to rewrite
  the entire local store can recompute the chain. There is no signing key or
  external checkpoint yet.
- Schema-v1/v2 receipts before the first sealed receipt remain unsealed legacy
  evidence; only the legacy tail referenced by the first sealed entry is
  directly protected from later modification.
- Fingerprinting reads all untracked file contents and may be slow in large
  repositories.
- Environment overrides are intentionally stored verbatim for reproducibility;
  users must not place secrets in manifests or publish reports containing them.
- Output written directly by parallel child commands can interleave on the
  terminal; ProofRun's own per-check summaries remain ordered.
- Checks that mutate shared files may race when run in parallel. `--jobs 1`
  remains the safe choice for suites whose commands are not independent.

## Recommended next step

Add structured `verify --json` output so agents and CI can consume suite and
per-check results without parsing terminal prose.

## Important decisions

- Local-first and zero runtime dependencies remain the initial wedge.
- Check working directories are relative to the repository invocation root and
  cannot escape it, including through symlinks.
- All selected check contexts are validated before suite execution to avoid
  partial evidence caused by a manifest configuration error.
- Receipts record only configured environment overrides, not the inherited host
  environment, balancing reproducibility with machine-data exposure.
- Receipt locks are sibling files managed by the operating system and remain
  present for reuse; lock ownership, and therefore writer exclusion, is
  automatically released when the process closes or exits.
- Check execution stays outside the receipt lock to preserve concurrency; only
  chain-tail reading, sealing, and append are serialized.
- `verify --jobs N` accepts positive integers and defaults to one; at most `N`
  checks are submitted at a time.
- Parallel result summaries follow manifest order for stable output, while the
  hash chain follows actual receipt completion order.
- Parallel fail-fast is observation-based: no new work is launched after a
  failure is seen, but already-started checks complete and retain their proof.
- Unix readers use shared locks for concurrent snapshots; Windows readers use
  the platform's short exclusive file lock because its standard library does
  not expose a shared mode.
- Path limits are presentation-only, apply across tracked paths before
  untracked paths in stable order, and never truncate receipt or JSON data.
- Evidence is invalidated by commit or working-tree changes, age, or a broken
  receipt chain.
- Receipts stay ignored by Git while product decisions and run handoffs are
  committed; schema changes remain backward-compatible at read time.

# ProofRun status

## Current product idea

ProofRun is a local-first CLI that records verification receipts for existing
development commands and binds them to the exact Git working state they covered.

## Current product shape

The dependency-free Python CLI has six commands: `run`, `verify`, `status`,
`audit`, `report`, and `history`. Receipts stay in append-only JSON Lines under
the ignored `.proofrun/` directory. Manifest checks can run from distinct
repository subdirectories with explicit environment overrides. Schema-v4
receipts preserve that execution context alongside Git snapshots, file-level
drift details, canonical SHA-256 hashes, and links to prior receipts. A
repository-local OS lock serializes the load-link-append critical section so
concurrent writers preserve one ordered chain without serializing command
execution; readers coordinate with the lock for consistent snapshots. Status
explains whether evidence still applies, audit detects local receipt-chain
damage, and report packages both views into a Markdown handoff.
Human status and reports cap invalidating paths at 10 by default with explicit
overflow counts; structured JSON remains complete.

## Completed today

- Added a cross-process receipt-store lock using standard-library OS primitives
  on Unix and Windows.
- Restricted locking to receipt loading, hash linking, and append, leaving slow
  verification commands outside the critical section.
- Added a widened eight-writer concurrency regression proving every append is
  retained and the resulting chain audits as fully valid.
- Coordinated readers through the same lock so status, audit, history, and
  report cannot observe a partially written final receipt.
- Expanded the suite to 21 tests, bumped the package to version 0.7.0, and
  documented lock behavior and lifecycle.

## Changed since the previous run

Simultaneous ProofRun processes can no longer read the same chain tail and
append competing successors. Writers queue only for the brief persistence
operation, and operating-system lock ownership prevents a crashed process from
leaving an owned stale lock behind.

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

## Recommended next step

Add bounded parallel manifest execution (for example, `verify --jobs N`) now
that concurrent check completions can safely append to one receipt chain.

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
- Unix readers use shared locks for concurrent snapshots; Windows readers use
  the platform's short exclusive file lock because its standard library does
  not expose a shared mode.
- Path limits are presentation-only, apply across tracked paths before
  untracked paths in stable order, and never truncate receipt or JSON data.
- Evidence is invalidated by commit or working-tree changes, age, or a broken
  receipt chain.
- Receipts stay ignored by Git while product decisions and run handoffs are
  committed; schema changes remain backward-compatible at read time.

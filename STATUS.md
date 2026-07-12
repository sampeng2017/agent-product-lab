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
drift details, canonical SHA-256 hashes, and links to prior receipts. Status
explains whether evidence still applies, audit detects local receipt-chain
damage, and report packages both views into a Markdown handoff.

## Completed today

- Added optional `cwd` and `[checks.<name>.env]` manifest settings for
  multi-package and context-sensitive verification commands.
- Made commands inherit the host process environment and deterministically
  apply the configured string overrides.
- Added strict validation for unsupported keys, invalid environment names and
  values, absolute or parent-traversing paths, symlink escapes, and missing
  directories. All selected directories are validated before any check runs.
- Kept Git coverage anchored to the repository invocation root even when a
  command executes in a subdirectory.
- Added schema-v4 receipt context and displayed it in Markdown reports; bumped
  the package to version 0.5.0.
- Added coverage for execution behavior, receipt/report metadata, validation,
  suite atomicity before execution, and the dependency-free Python 3.10 parser.

## Changed since the previous run

ProofRun manifests no longer need shell wrappers such as `cd packages/api &&`
or inline environment assignments. Checks now describe execution context as
structured, validated data, and the resulting evidence shows reviewers exactly
where and with which overrides a command ran.

## Known issues and incomplete work

- Hash chaining is tamper-evident, not authenticated: someone able to rewrite
  the entire local store can recompute the chain. There is no signing key or
  external checkpoint yet.
- Schema-v1/v2 receipts before the first sealed receipt remain unsealed legacy
  evidence; only the legacy tail referenced by the first sealed entry is
  directly protected from later modification.
- Concurrent writers are not serialized, so simultaneous ProofRun processes
  could compute the same previous hash and create a forked or reordered store.
- Fingerprinting reads all untracked file contents and may be slow in large
  repositories.
- Long invalidation lists can make Markdown reports noisy.
- Environment overrides are intentionally stored verbatim for reproducibility;
  users must not place secrets in manifests or publish reports containing them.

## Recommended next step

Add a concise invalidation summary with a configurable path display limit and
overflow count, keeping terminal status and Markdown reports useful in large
repositories without losing the full structured JSON detail.

## Important decisions

- Local-first and zero runtime dependencies remain the initial wedge.
- Check working directories are relative to the repository invocation root and
  cannot escape it, including through symlinks.
- All selected check contexts are validated before suite execution to avoid
  partial evidence caused by a manifest configuration error.
- Receipts record only configured environment overrides, not the inherited host
  environment, balancing reproducibility with machine-data exposure.
- Evidence is invalidated by commit or working-tree changes, age, or a broken
  receipt chain.
- Receipts stay ignored by Git while product decisions and run handoffs are
  committed; schema changes remain backward-compatible at read time.

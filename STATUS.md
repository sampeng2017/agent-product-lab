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
damage, and report packages both views into a Markdown handoff. Human status
and reports cap invalidating paths at 10 by default with explicit overflow
counts; structured JSON remains complete.

## Completed today

- Added a shared, deterministic path-display limiter for terminal status and
  Markdown reports.
- Added `--path-limit N` to `status` and `report`, with a concise 10-path
  default, overflow counts, and a zero-path summary mode.
- Kept `status --json` lossless: it returns every tracked and untracked path
  even when `--path-limit` is supplied.
- Added end-to-end regression coverage across human status, JSON status, and
  Markdown rendering; the suite now contains 19 tests.
- Bumped the package to version 0.6.0 and documented the presentation contract.

## Changed since the previous run

Large working-tree changes no longer flood terminals or review handoffs.
Reviewers see a representative stable prefix plus an exact omitted-path count,
while scripts consuming JSON retain the complete invalidation detail.

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
- Environment overrides are intentionally stored verbatim for reproducibility;
  users must not place secrets in manifests or publish reports containing them.

## Recommended next step

Serialize concurrent receipt writers with a repository-local lock so two
simultaneous ProofRun commands cannot compute the same previous hash and fork
or reorder the receipt chain.

## Important decisions

- Local-first and zero runtime dependencies remain the initial wedge.
- Check working directories are relative to the repository invocation root and
  cannot escape it, including through symlinks.
- All selected check contexts are validated before suite execution to avoid
  partial evidence caused by a manifest configuration error.
- Receipts record only configured environment overrides, not the inherited host
  environment, balancing reproducibility with machine-data exposure.
- Path limits are presentation-only, apply across tracked paths before
  untracked paths in stable order, and never truncate receipt or JSON data.
- Evidence is invalidated by commit or working-tree changes, age, or a broken
  receipt chain.
- Receipts stay ignored by Git while product decisions and run handoffs are
  committed; schema changes remain backward-compatible at read time.

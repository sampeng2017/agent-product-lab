# ProofRun status

## Current product idea

ProofRun is a local-first CLI that records verification receipts for existing
development commands and binds them to the exact Git working state they covered.

## Current product shape

The repository contains a dependency-free Python CLI with four commands:
`run`, `verify`, `status`, and `history`. Receipts use append-only JSON Lines
under `.proofrun/`, which stays local by default. `verify` reads a
`proofrun.toml` manifest and records a receipt for each named check. `status`
now reports which tracked and untracked paths invalidated the latest proof when
that receipt was recorded by the current schema.

## Completed today

- Extended the receipt Git snapshot to retain tracked-change and untracked-file
  digests alongside the aggregate fingerprint.
- Made `proofrun status` explain stale working-tree proofs with concrete path
  names instead of only saying the tree changed.
- Kept old schema receipts readable, falling back to the previous generic
  explanation when path detail is unavailable.
- Added tests for tracked-path drift, untracked-path drift, and backward
  compatibility with older receipts.
- Updated the docs and product notes to make file-level invalidation reporting
  part of the current product shape.

## Changed since the previous run

ProofRun moved from generic stale/valid answers to actionable invalidation
reporting. The latest receipts now capture enough Git-state detail for `status`
to show which files changed after a verification run.

## Known issues and incomplete work

- Fingerprinting still reads all untracked file contents and may be slow in
  large repositories.
- Receipts created before schema version 2 cannot name invalidating files
  because they only stored the aggregate fingerprint.
- Receipts are not cryptographically chained or shareable as a report.
- The manifest only supports per-check commands today; there is no first-class
  per-check environment or working-directory override.

## Recommended next step

Add tamper-evident receipt chaining and a compact export/report format so local
proof can be inspected or handed off without opening the raw JSON Lines store.

## Important decisions

- Local-first and zero runtime dependencies for the initial wedge.
- Evidence is invalidated by commit or working-tree changes and by age.
- Receipts are ignored by Git; product decisions and run handoffs are committed.
- The suite workflow is declarative via `proofrun.toml`, but each check still
  produces its own append-only receipt.
- Receipt schema changes should remain backward-compatible at read time so old
  local proof is not discarded when richer evidence is added later.

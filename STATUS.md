# ProofRun status

## Current product idea

ProofRun is a local-first CLI that records verification receipts for existing
development commands and binds them to the exact Git working state they covered.

## Current product shape

The repository contains a dependency-free Python CLI with five commands:
`run`, `verify`, `status`, `audit`, and `history`. Receipts use append-only JSON
Lines under `.proofrun/`, which stays local by default. `verify` reads a
`proofrun.toml` manifest and records a receipt for each named check. `status`
explains whether current proof remains applicable and which paths invalidated
it. New schema-v3 receipts carry a SHA-256 content hash and the digest of the
previous receipt; `audit` verifies that chain while identifying older receipts
as readable but unsealed.

## Completed today

- Added canonical receipt hashing and previous-receipt links so edits, interior
  deletion, insertion, and reordering become visible once a chain is established.
- Added `proofrun audit` with human-readable and JSON output plus a nonzero exit
  when any sealed receipt or link is invalid.
- Made `proofrun status` mark the latest proof stale when it is downstream of a
  chain failure, instead of trusting evidence from a damaged store.
- Preserved schema-v1/v2 compatibility: legacy entries remain readable and the
  first schema-v3 receipt seals the legacy store's current tail.
- Added coverage for valid chains, tampering propagation, and legacy migration;
  bumped the package to version 0.3.0 and documented the trust boundary.

## Changed since the previous run

ProofRun now verifies the integrity of its own evidence store. Previously,
receipts were append-only by convention but edits to the JSON Lines file were
not detectable. Each new receipt is now sealed and linked, and both a dedicated
audit command and normal status assessment account for chain integrity.

## Known issues and incomplete work

- Hash chaining is tamper-evident, not authenticated: someone able to rewrite
  the entire local store can recompute the chain. There is no signing key or
  external checkpoint yet.
- Schema-v1/v2 receipts before the first sealed receipt are reported as
  unsealed; only the legacy tail referenced by the first schema-v3 entry is
  directly protected from later modification.
- Concurrent writers are not serialized, so simultaneous ProofRun processes
  could compute the same previous hash and create a forked or reordered store.
- Fingerprinting still reads all untracked file contents and may be slow in
  large repositories.
- There is no compact shareable report, and the manifest has no first-class
  per-check environment or working-directory override.

## Recommended next step

Add a deterministic Markdown export that includes current proof status, check
metadata, invalidating paths, and receipt-chain audit state. This would make the
now-verifiable local evidence useful in code review and agent handoffs without
requiring readers to inspect raw JSON.

## Important decisions

- Local-first and zero runtime dependencies for the initial wedge.
- Evidence is invalidated by commit or working-tree changes, age, or a broken
  receipt chain.
- SHA-256 chaining provides local tamper evidence but is explicitly not
  presented as a digital signature or protection from full-store replacement.
- Receipts are ignored by Git; product decisions and run handoffs are committed.
- The suite workflow is declarative via `proofrun.toml`, but each check still
  produces its own append-only receipt.
- Receipt schema changes remain backward-compatible at read time so old local
  proof is not discarded when richer evidence is added later.

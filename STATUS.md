# ProofRun status

## Current product idea

ProofRun is a local-first CLI that records verification receipts for existing
development commands and binds them to the exact Git working state they covered.

## Current product shape

The dependency-free Python CLI has six commands: `run`, `verify`, `status`,
`audit`, `report`, and `history`. Receipts stay in append-only JSON Lines under
the ignored `.proofrun/` directory. Manifest-driven checks produce schema-v3
receipts with Git snapshots, file-level drift details, canonical SHA-256 hashes,
and links to prior receipts. Status explains whether evidence still applies,
audit detects local receipt-chain damage, and report packages both views into a
Markdown handoff.

## Completed today

- Added `proofrun report` with stdout and `--output PATH` modes.
- Included repository state, evidence policy, current valid-check count, receipt
  audit totals, and latest per-check result and command metadata in the export.
- Included tracked and untracked invalidating paths when the working tree has
  moved beyond the recorded proof.
- Kept damaged stores inspectable while returning a nonzero exit code, allowing
  automation to distinguish an exported warning report from trusted evidence.
- Added deterministic-rendering and CLI tests, created the requested `To-Sam/`
  communication folder, and bumped the package to version 0.4.0.

## Changed since the previous run

ProofRun evidence no longer has to be interpreted through terminal output or
raw JSON. A single command now creates a portable Markdown snapshot suitable
for a pull request description, review artifact, or agent handoff, using the
same status and chain-integrity rules as the interactive commands.

## Known issues and incomplete work

- Hash chaining is tamper-evident, not authenticated: someone able to rewrite
  the entire local store can recompute the chain. There is no signing key or
  external checkpoint yet.
- Schema-v1/v2 receipts before the first sealed receipt remain unsealed legacy
  evidence; only the legacy tail referenced by the first schema-v3 entry is
  directly protected from later modification.
- Concurrent writers are not serialized, so simultaneous ProofRun processes
  could compute the same previous hash and create a forked or reordered store.
- Fingerprinting reads all untracked file contents and may be slow in large
  repositories.
- Long invalidation lists can make Markdown reports noisy.
- Manifest checks cannot yet set first-class environment variables or working
  directories.

## Recommended next step

Add per-check `cwd` and `env` options to `proofrun.toml`, with strict validation
and receipt metadata that records the effective execution context. This unlocks
real multi-package repositories while preserving reproducible proof.

## Important decisions

- Local-first and zero runtime dependencies remain the initial wedge.
- Evidence is invalidated by commit or working-tree changes, age, or a broken
  receipt chain.
- Markdown reports are snapshots, not signed attestations; a broken chain is
  visible in the report and makes the command exit nonzero.
- Report ordering is stable and rendering accepts a fixed assessment time for
  deterministic testing; live age and report timestamps intentionally advance.
- Receipts stay ignored by Git while product decisions and run handoffs are
  committed.
- Receipt schema changes remain backward-compatible at read time.

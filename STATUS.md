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
order and append receipts in completion order. `verify --json` emits a
versioned suite document with complete receipts and explicit skip accounting;
check output moves to standard error so standard output remains valid JSON.
Schema-v4 receipts preserve the execution context alongside Git snapshots,
file-level drift details, canonical SHA-256 hashes, and links to prior receipts.
A repository-local OS lock
serializes the load-link-append critical section so concurrent writers preserve
one ordered chain without serializing command execution; readers coordinate
with the lock for consistent snapshots. Status explains whether evidence still
applies, audit detects local receipt-chain damage, and report packages both
views into a Markdown handoff.
Human status and reports cap invalidating paths at 10 by default with explicit
overflow counts; structured JSON remains complete.

## Completed today

- Added `proofrun verify --json` with a versioned suite-level contract,
  manifest-ordered check results, complete receipts, and explicit selected,
  executed, passed, failed, and skipped counts.
- Preserved the suite's real nonzero exit code and listed checks skipped by
  fail-fast so automation can distinguish failure from non-execution.
- Routed child standard output to standard error in JSON mode, preventing noisy
  checks from corrupting the machine-readable document without hiding logs.
- Added end-to-end noisy-command coverage plus fail-fast JSON contract tests;
  expanded the suite from 25 to 27 tests.
- Bumped the package to version 0.9.0 and documented the structured output
  behavior for agent and CI consumers.

## Changed since the previous run

Agents and CI can now consume verification results without parsing terminal
prose. The contract includes both aggregate accounting and the underlying
receipts, while existing human output and check execution semantics remain
unchanged.

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
- Structured verification intentionally preserves check standard error as live
  terminal output; parallel checks can still interleave those diagnostics.
- `status` reports stale proof but always exits zero, so it cannot yet serve as
  an enforceable acceptance gate by itself.

## Recommended next step

Add `status --require-valid` with optional named-check selection and a clear
nonzero exit contract for missing or stale proof, giving agents and CI an
enforceable acceptance gate.

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
- Structured verification uses a separately versioned schema, includes full
  receipts, and preserves the same manifest ordering and process exit code as
  human output.
- In JSON mode, child standard output is redirected to standard error; child
  standard error already uses that stream, leaving standard output as exactly
  one parseable JSON document.
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

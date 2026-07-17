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
A named `status --require-valid` selection now acts as a process gate: missing
proof is represented explicitly, while stale, missing, or empty-store
assessments return a nonzero exit code without changing normal status behavior.
A repository-local OS lock
serializes the load-link-append critical section so concurrent writers preserve
one ordered chain without serializing command execution; readers coordinate
with the lock for consistent snapshots. Status explains whether evidence still
applies, audit detects local receipt-chain damage, and report packages both
views into a Markdown handoff.
Human status and reports cap invalidating paths at 10 by default with explicit
overflow counts; structured JSON remains complete.

## Completed today

- Added optional check names to `proofrun status`, preserving request order and
  returning explicit `missing` assessments for names without receipts.
- Added `status --require-valid`: it exits 0 only when every selected proof is
  valid, 1 for stale, missing, or an empty unscoped store, and leaves existing
  informational status calls at exit 0.
- Kept the gate compatible with both human and JSON output, including complete
  stale reasons and a stable missing-proof object with a null receipt.
- Added regressions for a selected valid proof, mixed stale/missing JSON, and
  empty-store rejection; expanded the suite from 27 to 30 tests.
- Bumped the package to version 1.0.0 and documented the acceptance contract.

## Changed since the previous run

Agents and CI can now enforce that specific named evidence still applies to the
current repository instead of merely inspecting status output. Missing proof is
distinguishable from stale proof, and existing observational workflows remain
backward-compatible.

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
- Receipts capture Git state after a command finishes. If a check mutates the
  repository, the receipt may cover a post-command state that the command did
  not fully validate; pre/post execution-state comparison is not implemented.

## Recommended next step

Capture Git state before and after each command and make repository-mutating
checks explicit, preventing a passing command from accidentally claiming proof
for code it changed but did not subsequently verify.

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
- Named status selection follows the caller's order and represents unknown
  names as missing evidence rather than treating them as invalid arguments.
- `status --require-valid` uses exit 1 for an unmet evidence requirement and
  preserves exit 2 for malformed input or receipt-store errors; without the
  flag, status remains informational and exits 0.
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

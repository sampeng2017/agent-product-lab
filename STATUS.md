# ProofRun status

## Current product idea

ProofRun is a local-first CLI that records verification receipts for existing
development commands and binds them to the exact Git working state they covered.

## Current product shape

The dependency-free Python CLI has seven commands: `init`, `run`, `verify`,
`status`, `audit`, `report`, and `history`. `init` detects a single Python,
Node.js, Rust, or Go project (or accepts an explicit command), writes a starter
manifest, and can generate the proven GitHub Actions integration when given a
concrete pip install source. It preflights every target and refuses to overwrite
existing configuration unless `--force` is explicit. Receipts stay in
append-only JSON Lines under the ignored `.proofrun/` directory. Manifest
checks can run from distinct repository subdirectories with explicit
environment overrides, sequentially or with bounded `--jobs N` concurrency.
Parallel suites report results in manifest order and append receipts in
completion order. `verify --json` emits a
versioned suite document with complete receipts and explicit skip accounting;
check output moves to standard error so standard output remains valid JSON.
Schema-v5 receipts preserve the execution context, pre/post Git snapshots, the
real command exit code, file-level drift and in-command mutation details,
canonical SHA-256 hashes, and links to prior receipts. A passing check that
changes repository state is rejected with exit 1, so its post-command snapshot
cannot silently claim evidence for code the check did not fully verify.
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
The checked-in GitHub Actions workflow now exercises this full contract on
pushes and pull requests: it preserves structured output and a Markdown report
as run evidence, publishes the report as the job summary, and finishes with a
named validity gate.

## Completed today

- Added `proofrun init` with conservative Python/unittest, Python/pytest,
  Node.js, Rust, and Go command detection plus an explicit custom-command path.
- Added optional GitHub Actions generation that requires an explicit pip
  requirement for ProofRun, avoiding an unsafe assumption about package
  publication or ownership.
- Preflighted all selected targets before writing, rejected ambiguous or unknown
  project types, preserved existing files by default, and added explicit
  `--force` replacement.
- Added four end-to-end bootstrap regressions covering detection, overwrite
  refusal and force, all-target conflict safety, workflow generation, and the CI
  install-source requirement, plus detection coverage across supported project
  types; the suite now has 37 tests.
- Parsed a generated workflow as YAML and exercised init in a disposable
  repository. Bumped ProofRun to 1.2.0.
- Processed Sam's GitHub remote offer and left a concrete, non-blocking handoff
  request under `To-Sam/` for the next adoption step.

## Changed since the previous run

ProofRun's proven local and CI workflow is now adoptable through a first-class
command instead of manual configuration copying. The scaffold is conservative:
it will not guess across mixed ecosystems, overwrite user files silently, or
emit a workflow that assumes an unspecified ProofRun distribution source.

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
  remains the safe choice for suites whose commands are not independent; safe
  mutation detection can conservatively reject a check because another parallel
  check changed repository state during its execution window.
- Structured verification intentionally preserves check standard error as live
  terminal output; parallel checks can still interleave those diagnostics.
- Pre/post fingerprinting doubles the Git-state inspection work around each
  check, which may be noticeable when many large untracked files are present.
- Mutation detection compares Git-visible state at check boundaries; ignored
  files and transient changes fully restored before exit are not detected.
- The example workflow targets GitHub.com and current GitHub-hosted runners;
  its `upload-artifact` version is not compatible with GitHub Enterprise Server.
- The workflow has been syntax-checked and its ProofRun command sequence was
  executed locally, but no hosted GitHub Actions run is recorded yet.
- ProofRun does not yet have a configured remote or tagged public/private pip
  install source, so generated CI requires the adopter to pass `--ci-install`.
- Project detection is intentionally narrow and has only local fixture coverage;
  real-world monorepos and nonstandard test layouts require an explicit command.

## Recommended next step

After Sam provides the requested remote, configure it, push the repository,
create a versioned installation reference, and validate the checked-in workflow
on hosted GitHub Actions. Then use that pinned reference to test the generated
`proofrun init --github-actions` output in a separate sample repository.

## Important decisions

- Local-first and zero runtime dependencies remain the initial wedge.
- Bootstrap detection only succeeds for one recognized ecosystem; ambiguity or
  no match requires the user to state the verification command explicitly.
- Scaffold target conflicts are checked as a group before any write. Existing
  files require explicit `--force`, and generated CI requires an explicit,
  single-line pip install requirement for ProofRun.
- A successful command that changes Git state is a rejected proof with exit 1;
  intentional mutators should run before a separate verifier. Failed mutators
  preserve the command's original nonzero exit code.
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
- CI evidence files belong outside the checkout so generating JSON and Markdown
  cannot change the repository state covered by a verification receipt.
- Report, artifact, and proof-gate steps use GitHub's `always()` condition so
  diagnostics survive a failed verification; the suite exit and final audit or
  named status gate can each fail the job.
- The repository workflow grants only `contents: read` and pins the current
  supported major versions of GitHub's official checkout, Python setup, and
  artifact actions.
- Unix readers use shared locks for concurrent snapshots; Windows readers use
  the platform's short exclusive file lock because its standard library does
  not expose a shared mode.
- Path limits are presentation-only, apply across tracked paths before
  untracked paths in stable order, and never truncate receipt or JSON data.
- Evidence is invalidated by commit or working-tree changes, age, or a broken
  receipt chain, and permanently rejected when the check itself mutated the
  repository.
- Sam's suggestion to pivot once improvement ideas are exhausted is accepted;
  ProofRun continues for now because mutation safety and agent/CI adoption remain
  concrete product work, with the repository structure to be revisited at pivot.
- Receipts stay ignored by Git while product decisions and run handoffs are
  committed; schema changes remain backward-compatible at read time.

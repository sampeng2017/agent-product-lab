# ProofRun status

> Frozen on 2026-08-20 as a completed v1.8.1 local MVP. This file preserves the
> final product-specific status; active portfolio direction lives in the root
> `STATUS.md`.

## Current product idea

ProofRun is a local-first CLI that records verification receipts for existing
development commands and binds them to the exact Git working state they covered.

## Current product shape

The dependency-free Python CLI has seven commands: `init`, `run`, `verify`,
`status`, `audit`, `report`, and `history`. `init` detects a single Python,
Node.js, Rust, or Go project (or accepts an explicit command), writes a starter
manifest, and can generate the proven GitHub Actions integration when given a
concrete pip install source. Node detection requires a real test script and
chooses npm, pnpm, Yarn, or Bun from `packageManager` or unambiguous lockfile
evidence instead of blindly assuming npm. Generated CI for detected Node
projects now sets up Node.js, pnpm, Yarn/Corepack, or Bun as appropriate and
installs dependencies, choosing a lockfile-strict install when possible. It
preflights every target and refuses to overwrite existing configuration unless
`--force` is explicit. A dry-run mode exposes the chosen command and
create/overwrite actions without changing disk; its versioned JSON form also
includes the exact generated content for agent inspection. Detected Python
scaffolds choose `python3` or `python` from the interpreter
family running ProofRun, suppress bytecode writes, and disable pytest's cache
provider so incidental test-runner artifacts do not invalidate fresh proof.
Generated Python CI installs detected `requirements.txt`,
`requirements-dev.txt`, and `requirements-test.txt` inputs, plus pytest when
that runner is selected, before ProofRun snapshots repository state.
Detected Rust scaffolds route Cargo build output to
`.proofrun/cargo-target` through a recorded manifest environment override, so a
repository does not need to ignore `target/` before its first verification.
Receipts
stay in append-only JSON Lines under the ignored `.proofrun/` directory. Manifest
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
Git metadata, branch/head discovery, and changed-path enumeration now use one
NUL-safe porcelain-v2 snapshot instead of multiple full-tree scans. Exact
untracked content hashes are streamed in bounded-memory chunks; normal-path
fingerprints remain byte-compatible with earlier receipts.
Tracked patch fingerprints are also batched: one patch and one NUL-safe name
scan for each of the working tree and index replace two Git subprocesses per
changed path. ProofRun splits the unchanged patch bytes back into per-file
digests and retains the legacy path as a compatibility fallback when unusual
Git output cannot be framed safely.
The checked-in GitHub Actions workflow now exercises this full contract on
pushes and pull requests: it preserves structured output and a Markdown report
as run evidence, publishes the report as the job summary, and finishes with a
named validity gate.

## Completed today

- Checked Git history/status, all product and handoff documentation, tests,
  implementation, automation memory, and `To-Sam/`; the optional remote request
  remains unanswered and local work continued without blocking.
- Attempted native pnpm and Yarn workflow adoption through the installed
  Corepack runtime. Both package-manager downloads were blocked by the host's
  registry certificate chain, while the installed Bun runtime remained usable.
- Inspected the current official pnpm setup contract and active v6 regressions,
  finding that generated workflows relied on action-side inference that can
  ignore a repository's declared pnpm version.
- Parsed and retained declared Node package-manager versions, rejected malformed
  declarations without `manager@version`, and made generated pnpm setup pass the
  declared version explicitly. Structured init previews now expose the version.
- Added declared-version, integrity-suffix, malformed-declaration, workflow, and
  preview regressions. The suite grew from 52 to 53 tests and the package
  version is now 1.8.1.

## Changed since the previous run

Generated pnpm CI now deterministically honors the version already declared by
the adopter. Previously, ProofRun omitted the setup action's version input for a
declared project and trusted action-side inference; current upstream v6 issues
show that inference can select the wrong pnpm release. Lockfile-only pnpm
projects retain the documented explicit `latest` fallback.

## Known issues and incomplete work

- Hash chaining is tamper-evident, not authenticated: someone able to rewrite
  the entire local store can recompute the chain. There is no signing key or
  external checkpoint yet.
- Schema-v1/v2 receipts before the first sealed receipt remain unsealed legacy
  evidence; only the legacy tail referenced by the first sealed entry is
  directly protected from later modification.
- Exact fingerprinting still reads all untracked file contents and is linear in
  their total byte size, although reads are now streamed in bounded memory.
- Batched tracked diffing passes all changed paths as Git pathspec arguments;
  extremely large path sets may approach the operating system command-line
  length limit. The compatibility fallback also remains intentionally slower
  for diff-driver or merge output that cannot be mapped one block per path.
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
- Pre/post fingerprinting necessarily performs exact Git-state inspection at
  both check boundaries; the metadata scans are consolidated, but content bytes
  must still be read twice when large untracked inputs remain unchanged.
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
- Native Rust adoption remains unverified on this host because Cargo is not
  installed. The generated build-output redirect has executable integration
  coverage using a deterministic Cargo stand-in. Cargo may still create or
  update `Cargo.lock`; adopters should stabilize that Git-visible input before
  verification rather than having ProofRun hide it.
- Python workflow dependency discovery intentionally recognizes only
  `requirements.txt`, `requirements-dev.txt`, and `requirements-test.txt`.
  Projects using extras, lock tools, or nonstandard files still need a manually
  tailored workflow after scaffolding. Minimal pytest workflows without a
  requirements constraint install the current pytest release.
- Lockfile-only pnpm, Yarn, and Bun projects do not provide an exact
  package-manager version. Generated CI can provision them, but the setup tool's
  current default is used; add a `packageManager` declaration to pin the tool.
- Native pnpm and Yarn end-to-end adoption remain unverified on this host because
  Corepack cannot validate the local registry certificate chain. Workflow
  rendering and package-manager selection remain covered without downloads.
- Package-manager setup is inferred only for automatically detected Node
  presets. Explicit custom commands are intentionally opaque, so adopters must
  add any required runtime/dependency setup to the generated workflow.
- A detected Node project without a lockfile uses the manager's normal install
  command, so dependency resolution is not reproducible until a lockfile is
  committed.

## Recommended next step

After Sam provides the requested remote, configure it, push the repository,
create a versioned installation reference, and validate the checked-in workflow
on hosted GitHub Actions. If the remote remains unavailable, run the Rust
adoption fixture with a native Cargo runtime when one becomes available;
otherwise complete native pnpm and Yarn fixtures when their runtimes can be
provisioned, then add a real Bun init-to-proof fixture with the installed runtime.

## Important decisions

- Local-first and zero runtime dependencies remain the initial wedge.
- Git porcelain v2 with `-z` is the single source for head, branch, dirty state,
  and changed paths. Content hashing remains exact, uses filesystem byte
  encoding for paths, and streams files rather than allocating them whole.
- Tracked state uses batched patch plus NUL-safe name output for the working tree
  and index. Patch blocks are hashed byte-for-byte in Git's matching name order;
  a framing mismatch triggers the legacy per-path algorithm for that scope.
- Bootstrap detection only succeeds for one recognized ecosystem; ambiguity or
  no match requires the user to state the verification command explicitly.
- Detected Python bootstrap mirrors the running interpreter's portable launcher
  family. `-B` prevents bytecode writes and pytest's cache provider is disabled
  because generated verification must not make its own clean proof stale.
- Generated Python workflows install conventional requirements files in stable
  base/development/test order and explicitly install pytest for a detected
  pytest preset. Setup remains outside ProofRun verification, and unfamiliar
  Python dependency conventions are not guessed.
- Detected preset environment overrides are rendered as manifest env tables and
  exposed in structured previews. Rust uses this path for `CARGO_TARGET_DIR`,
  while `Cargo.lock` stays Git-visible because it is verification input rather
  than disposable build output.
- Node bootstrap requires a real `scripts.test`; `packageManager` is
  authoritative when present, one recognized lockfile family is the fallback,
  and conflicting lockfile families require an explicit command. Declarations
  must use `manager@version`; an integrity suffix is retained in `package.json`
  but omitted from the setup action's semantic version input.
- Automatically detected Node presets carry package-manager and lockfile
  metadata into workflow rendering. Generated CI provisions the corresponding
  tool and installs dependencies before ProofRun snapshots verification state;
  explicit commands do not trigger inferred setup.
- Declared pnpm versions are sent to `pnpm/action-setup` explicitly rather than
  relying on its package metadata inference; lockfile-only projects request
  `latest` because no authoritative version is available.
- Detected Node workflows pin Node.js 24 and action majors. Lockfiles select
  strict installs; without a lockfile, normal install semantics are explicit.
- Scaffold target conflicts are checked as a group before any write. Existing
  files require explicit `--force`, and generated CI requires an explicit,
  single-line pip install requirement for ProofRun.
- Init dry runs use the exact same validated scaffold plan as real writes. Human
  output summarizes command and target actions; versioned JSON additionally
  carries exact contents, and JSON is intentionally unavailable in write mode.
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

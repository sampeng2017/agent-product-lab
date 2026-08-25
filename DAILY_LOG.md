# Daily log

## 2026-07-08 — First run

Started from an empty Git repository. Researched current developer trust,
consumer subscription, and adult-learning needs, then evaluated three product
ideas: ProofRun, Renewal Radar, and Friction Deck. Selected ProofRun because the
AI-code verification gap is concrete, current, and small enough to address with
a useful local prototype.

Built the first dependency-free Python CLI. `proofrun run` now executes a named
command and stores a JSON Lines receipt containing timing, outcome, command, and
Git state. `proofrun status` reports whether each latest successful check still
applies to the current code, and `proofrun history` exposes recent evidence.
Added tests for successful, failed, expired, and working-tree-invalidated
receipts, plus product and run documentation.

Current state: runnable MVP with all three initial tests passing. The next run
should add a declarative check manifest and suite execution.

## 2026-07-08 — Manifest-driven verification

Continued ProofRun rather than revisiting product selection. The highest-value
gap from the previous state was repeatability: checks could be recorded one at
a time, but there was no standard suite entry point to dogfood inside this
repository. Implemented `proofrun verify`, which reads `proofrun.toml`, runs
all or selected checks, records one receipt per check, and can stop on first
failure with `--fail-fast`.

Added a repository-level `proofrun.toml` containing the unit-test workflow and
expanded tests to cover manifest loading, check selection, and fail-fast suite
execution. Updated README and product docs to make `verify` the primary
development workflow. Validation this run used both
`PYTHONPATH=src python3 -m unittest discover -s tests -v` and
`PYTHONPATH=src python3 -m proofrun verify`, both of which passed.

Current state: the project now supports both ad hoc checks and declarative
suite execution with append-only receipts. The next run should make `status`
more actionable by showing which files invalidated the last proof.

## 2026-07-09 — File-level invalidation reporting

Continued ProofRun on the same product path. The highest-value gap after the
manifest workflow was actionability: `proofrun status` could tell me that proof
went stale, but not which files caused the drift. Implemented a richer Git
snapshot in each new receipt by storing tracked-change digests and untracked
file digests alongside the aggregate fingerprint.

Updated `assess_receipts()` so stale working-tree proofs now carry structured
tracked and untracked path lists, and changed the CLI output to print those
paths inline when available. Kept backward compatibility for schema-v1 receipts
by falling back to the original generic message when old receipts only contain
the coarse fingerprint. Expanded tests to cover tracked edits, untracked-file
creation, and legacy-receipt reading.

Validation this run used `PYTHONPATH=src python3 -m unittest discover -s tests
-v`, which passed. The next run should add tamper-evident receipt chaining
and/or a compact export format so proof can be inspected or shared without
reading raw JSON Lines.

## 2026-07-09 — Tamper-evident receipt chain

Continued ProofRun and addressed the trust gap identified in the prior run:
the receipt file was append-only by convention, but ProofRun could not detect
if stored evidence had been edited. Schema-v3 receipts now contain a canonical
SHA-256 content hash and the digest of the preceding receipt. The new
`proofrun audit` command checks both each receipt and chain continuity, supports
human-readable and JSON output, and returns a failure exit code for a broken
chain. `proofrun status` also refuses to treat proof downstream of a detected
chain failure as valid.

Backward compatibility remains intentional. Schema-v1/v2 entries are shown as
legacy unsealed evidence, and the first new receipt links to the current legacy
tail. Added tests for valid sealing and links, tampering propagation through a
later receipt, and migration from a legacy store. Documented that a local hash
chain is tamper-evident rather than a digital signature and bumped the package
to 0.3.0.

Validation passed with 12 unit tests, the manifest-driven `proofrun verify`
workflow, human and JSON `proofrun audit`, `proofrun status`, and
`git diff --check`. Dogfooding reported six historical unsealed receipts and a
valid sealed chain. The next run should build a deterministic Markdown export
containing status and audit evidence for review or agent handoff.

## 2026-07-10 — Review-ready Markdown reports

Continued ProofRun and completed the shareability step selected in the previous
run. Added `proofrun report`, which renders repository state, evidence policy,
receipt-chain audit totals, and the latest result and metadata for every check
as Markdown. Stale checks include their reasons and, when available, the exact
tracked and untracked paths that invalidated them. Reports go to stdout or an
explicit `--output` path.

The renderer has stable ordering and a controllable assessment time for
deterministic tests. A damaged receipt store is still rendered for diagnosis,
but `report` exits nonzero so CI or agent workflows cannot mistake that artifact
for trusted evidence. Added coverage for report contents, changed-path output,
deterministic rendering, file export, and invalid-chain exit behavior; the suite
now has 14 tests. Also created the requested `To-Sam/` communication folder and
bumped ProofRun to 0.4.0.

Validation used the unit suite, `compileall`, `git diff --check`, report help,
and a live report against this repository's eight stored receipts. The next run
should add strict per-check `cwd` and `env` manifest options and record the
effective execution context in each receipt.

## 2026-07-11 — Reproducible per-check execution contexts

Continued ProofRun and implemented the multi-package workflow selected in the
previous handoff. Manifest checks now accept a repository-relative `cwd` plus a
`[checks.<name>.env]` string table. Commands inherit the process environment,
apply those overrides, and execute from the declared directory while their Git
snapshot continues to cover the full repository invocation root.

Made configuration failures safe and predictable: unsupported fields, invalid
environment entries, parent traversal, absolute paths, symlink escapes, and
missing directories are rejected, and every selected context is validated
before the first check starts. Schema-v4 receipts record the configured working
directory and environment overrides, and Markdown reports expose both. The
Python 3.10 dependency-free TOML fallback supports the same nested environment
tables. Documentation warns that override values are stored verbatim and must
not contain secrets.

Expanded the suite from 14 to 18 tests, covering actual cwd/env execution,
receipt and report metadata, strict manifest errors, preflight atomicity, and
fallback parsing. Validation passed with the full unit suite, `compileall`, and
`git diff --check`. The next run should add a compact path summary/limit for
large invalidation sets while retaining full path data in JSON output.

## 2026-07-12 — Compact invalidation path summaries

Continued ProofRun and completed the large-change readability improvement from
the previous handoff. Human `status` output and Markdown reports now display at
most 10 invalidating paths per check by default, followed by an exact overflow
count. Both commands accept `--path-limit N`, including zero for count-only
summaries. A shared presentation helper keeps ordering and limit behavior
consistent across both views.

The limit is deliberately presentation-only. `status --json` still returns
every tracked and untracked invalidating path, even when `--path-limit` is also
provided, so existing automation remains lossless. Added end-to-end coverage
for a 12-file drift across terminal status, structured JSON, and Markdown; the
suite now has 19 tests. Bumped ProofRun to 0.6.0 and updated user and product
documentation.

Validation passed with the full unit suite, `compileall`, `git diff --check`,
manifest-driven `verify`, audit, status, and a Markdown report export. The next
run should serialize concurrent receipt writers with a repository-local lock
to prevent receipt-chain forks or reordering.

## 2026-07-13 — Serialized concurrent receipt writers

Continued ProofRun and closed the chain-integrity race identified in the prior
handoff. Receipt append now acquires an OS-managed sibling lock before reading
the current tail, computing the previous link, sealing the new receipt, and
writing it. Readers coordinate through the same lock and cannot observe a
partial final record. Command execution remains outside this narrow critical
section, so independent verification work is not unnecessarily serialized.
The lock uses standard-library primitives on Unix and Windows and is released
by the operating system when a process exits.

Added a deterministic concurrency regression that releases eight writers at
once and deliberately slows receipt hashing to widen the historical race. The
test verifies that all eight records survive and every link audits as valid. A
second regression holds a writer mid-append and proves a reader waits for the
complete receipt; the full suite now contains 21 tests. Bumped ProofRun to 0.7.0
and documented the lock path, lifecycle, portability, and threat boundary.

Validation passed with the full unit suite, `compileall`, `git diff --check`,
and the manifest-driven ProofRun workflow. A separate live stress check started
eight CLI processes against one temporary store; all eight receipts were
retained and the entire chain audited as valid. The next run should use the
now-safe writer path to add bounded parallel manifest execution such as
`proofrun verify --jobs N`.

## 2026-07-14 — Bounded parallel manifest verification

Continued ProofRun with no pivot and no active message from Sam. Added
`proofrun verify --jobs N`, which defaults to the existing sequential behavior
and runs no more than the requested positive number of checks concurrently.
The scheduler keeps user-facing results in manifest order while the locked
receipt store records actual completion order, preserving an accurate and valid
hash chain.

Defined fail-fast behavior for concurrent suites: once ProofRun observes a
failure it stops launching new checks, but checks already running are allowed to
finish and retain their receipts. Added deterministic regressions for the
worker bound, result ordering, parallel fail-fast, invalid worker counts, and
CLI argument wiring. Documented the risk of interleaved child output and shared
file mutation, and bumped the package to 0.8.0. The suite now has 25 tests.

Validation passed with the full unit suite, `compileall`, `git diff --check`,
CLI help inspection, manifest-driven `verify --jobs 2`, receipt-chain audit,
status, and Markdown report export. The next run should add structured
`verify --json` output so agents and CI can consume suite results without
parsing terminal prose.

## 2026-07-15 — Machine-readable suite results

Continued ProofRun with no pivot and no active message from Sam. Added
`proofrun verify --json`, which emits one versioned document containing the
suite state and exit code, selected/executed/passed/failed/skipped counts,
skipped check names, and manifest-ordered per-check results with their complete
receipts. Failed suites preserve the first failing check's exit code, and
parallel or fail-fast scheduling retains the semantics established in the
previous run.

Made the output safe for real-world automation rather than only quiet test
commands: in JSON mode, child standard output is routed to standard error, so
arbitrary check logs cannot corrupt the JSON on standard output. Logs remain
visible, and child standard error is unchanged. Added an end-to-end regression
using a noisy subprocess plus a fail-fast contract test that verifies skipped
names, counts, and exit behavior. Bumped ProofRun to 0.9.0; the suite now has 27
tests.

Validation passed with the full unit suite, compileall, diff checks, CLI help,
manifest-driven JSON verification, receipt-chain audit, status, and Markdown
report export. The next run should add `status --require-valid` with optional
named-check selection so agents and CI can enforce rather than merely inspect
fresh proof.

## 2026-07-16 — Enforceable proof-status gate

Continued ProofRun with no pivot and no active message from Sam. Added optional
named-check selection to `proofrun status`; selections retain caller order and
names without receipts produce explicit `missing` results in both terminal and
JSON output. Added `--require-valid` as an acceptance contract: it exits 0 only
when all selected evidence is valid, exits 1 for stale or missing evidence and
for an empty unscoped store, and preserves exit 2 for malformed input or store
errors. Existing status calls remain informational and continue to exit 0.

Added end-to-end regressions for selecting a valid check while ignoring an
unrelated failure, mixed stale/missing JSON output, and empty-store rejection.
The suite grew from 27 to 30 tests, the package reached version 1.0.0, and the
README and product roadmap now document the gate for agent and CI use.

Validation passed with the full unit suite, compileall, diff checks, status help
inspection, a live missing-proof gate probe, manifest-driven verification,
receipt-chain audit, gated status, and Markdown report export. The next run
should compare pre- and post-command Git state so a check that mutates the
repository cannot accidentally claim proof for code it did not fully test.

## 2026-07-17 — Mutation-safe verification receipts

Continued ProofRun after reading Sam's note encouraging a pivot when the current
idea has no valuable improvements left. The repository still documented a
specific trust flaw: a passing check could alter code and receive a valid
receipt for the post-command state even though that state was not necessarily
verified. Closed that gap rather than pivoting prematurely, and archived the
processed note under `To-Sam/archive/`.

Every check now captures Git state before and after command execution. Schema-v5
receipts record both snapshots, the command's real exit code, the effective
ProofRun exit code, and structured mutation evidence for commit changes plus
tracked and untracked paths. When an otherwise-passing command mutates the
repository, ProofRun rejects the proof with exit 1. A failing mutator keeps its
original command exit code. Status and Markdown reports mark this evidence stale
for the permanent reason `repository changed during check` and show the mutated
paths; terminal suite output calls the result rejected instead of merely failed.

Added regressions for successful non-mutators, passing tracked/untracked
mutators, failing mutators, status diagnostics, report evidence, and schema
sealing. The suite grew from 30 to 32 tests and the package version is now 1.1.0.
Validation covered the full unit suite, compileall, diff checks, manifest-driven
structured verification, receipt audit, the named validity gate, and Markdown
report generation. The next run should add a practical agent/CI integration
example that publishes structured verification and a Markdown proof artifact.

## 2026-07-18 — GitHub Actions proof publishing

Continued ProofRun and completed the adoption task from the prior handoff. Added
an active GitHub Actions workflow for pushes, pull requests, and manual runs. It
installs the package, captures the versioned `verify --json` document outside
the checkout, renders the Markdown report into GitHub's job summary, and uploads
both evidence files as a 14-day artifact. The report, upload, and proof-gate
steps use `always()` so a failed verification does not short-circuit evidence
publication, while the original suite exit remains failed. A final receipt
audit plus `status --require-valid unit` independently rejects stale, missing,
damaged, or unsuccessful proof.

The runner temp location is a deliberate part of the integration contract.
Writing JSON or Markdown into the checkout while ProofRun is observing it could
make an otherwise valid check look like a repository mutator. Documented this
constraint and how to adapt the named gate for another manifest. Updated the
product roadmap from CI exploration to a conservative bootstrap command that
can generate starter configuration without overwriting user files.

Validation used the existing 32-test suite, Ruby's YAML parser, a local
simulation of the evidence-producing commands with runner-temp and job-summary
files, JSON parsing, byte comparison of the generated report and summary,
receipt audit, and the named validity gate. The next run should add
`proofrun init` to scaffold a starter manifest and CI workflow safely.

## 2026-07-19 — Conservative repository bootstrap

Continued ProofRun and completed the adoption improvement selected in the prior
handoff. Added `proofrun init`, which recognizes a single Python/unittest,
Python/pytest, Node.js, Rust, or Go project and writes a starter manifest. Mixed
or unknown repositories fail with an actionable request for an explicit command
instead of receiving a misleading default. Users can set the check name or pass
the exact command after `--`.

The command preserves existing project configuration by default. It preflights
every selected destination before writing, reports all conflicts, and only
replaces files when `--force` is explicit. Optional `--github-actions`
generation reproduces the repository's structured verification, Markdown
evidence publication, audit, and validity gate. It deliberately requires
`--ci-install` with a concrete pip requirement so ProofRun does not claim a
package location or publisher that does not yet exist.

Added four CLI regressions covering automatic detection, overwrite refusal and
force, multi-target preflight, generated workflow content, and the install-source
requirement, plus detection coverage across supported project types. The suite
grew from 32 to 37 tests and the package version is now 1.2.0. A disposable
repository smoke test generated valid TOML and YAML. Sam
offered to create a GitHub remote; the processed note is archived and an active
request now explains how to hand back an empty repository URL.

Validation used the full unit suite, compileall, diff checks, CLI help, generated
YAML parsing, manifest-driven structured verification, receipt audit, the named
validity gate, and Markdown report export. The next run should connect Sam's
remote, establish a pinned installation reference, run hosted CI, and exercise
the generated workflow in a separate sample repository.

## 2026-07-20 — Package-manager-aware Node bootstrap

Continued ProofRun while the active request for Sam's GitHub remote remains
unanswered. Used the time for a local adoption fix: the initial Node detector
treated every `package.json` as proof that `npm test` was runnable. It now parses
the manifest, requires a non-empty `scripts.test`, rejects the default
"no test specified" placeholder, and returns an actionable explicit-command
fallback rather than creating configuration that is guaranteed to fail.

Node bootstrap now honors npm, pnpm, Yarn, and Bun. A supported
`packageManager` declaration is authoritative; otherwise a single recognized
lockfile family selects the command, no lockfile defaults to npm, and conflicting
manager lockfiles are rejected instead of guessed. Bun uses `bun run test` while
the other managers use their native `test` command. Added regression coverage
for declarations, lockfiles, absent and placeholder scripts, and ambiguous
manager evidence. The full suite now contains 39 tests and the package version
is 1.3.0.

Validation covered the focused detector tests, the full unit suite, compileall,
diff checks, package version inspection, CLI help, manifest-driven structured
verification, receipt audit, the named validity gate, and Markdown report
generation. When Sam supplies the remote, the next run should publish and test
the pinned workflow. If that remains blocked, the next local adoption feature
should be a dry-run or structured preview for `proofrun init`.

## 2026-07-21 — Side-effect-free init previews

Continued ProofRun while the active GitHub remote request remains unanswered and
completed the local adoption improvement from the prior handoff. Scaffold
validation and rendering are now represented as an immutable plan that is
applied only after the CLI decides to write. `proofrun init --dry-run` uses that
same plan to report the detected or explicit command and whether each target
would be created or overwritten, without touching the filesystem.

Added `init --dry-run --json` for agent consumption. Its versioned document
contains the check name, command source and preset, selected command, force
state, target actions, and exact generated contents. JSON is deliberately
rejected without dry-run so machine-readable preview output cannot be confused
with a successful write. Existing conflict rules still apply: previewing an
overwrite requires explicit `--force`, while neither new nor existing files are
changed.

Added four regressions covering detected human previews, exact structured
content with mixed overwrite/create actions, the JSON safety guard, and a target
appearing between planning and apply. The suite now has 43 tests and the package
version is 1.4.0. Full unit tests,
compileall, diff checks, CLI help inspection, and a live structured preview
against this repository passed. The next run should publish and exercise hosted
CI if Sam supplies the remote; otherwise generated workflows should provision
pnpm, Yarn, or Bun when bootstrap selects those package managers.

## 2026-07-22 — Runnable Node CI scaffolds

Continued ProofRun while the active request for Sam's GitHub remote remains
unanswered. Closed the next documented local adoption gap: Node bootstrap could
select npm, pnpm, Yarn, or Bun, but the generated workflow neither provisioned
the selected tool nor installed project dependencies before running the test
command.

Detected Node presets now carry package-manager declaration and lockfile
metadata into workflow rendering. Generated CI sets up Node.js 24 for npm, pnpm,
and Yarn, uses the current official pnpm setup action, enables Corepack for
Yarn, and uses the official Bun setup action for Bun. It installs dependencies
before ProofRun verification, selecting `npm ci`, frozen pnpm/Yarn installs, or
`bun ci` when a matching lockfile exists and a normal install otherwise.
Structured init previews now expose the detected package manager alongside the
exact generated workflow.

Added a workflow matrix regression covering npm, declared pnpm, lockfile-only
pnpm, Yarn, and Bun setup/install behavior, including the absence of irrelevant
setup actions. The suite grew from 43 to 44 tests and the package version is now
1.5.0. Official setup behavior and current action majors were checked against
the setup-node, pnpm/action-setup, and Bun documentation. Full validation
covered the unit suite, Python compilation, diff checks, generated YAML for all
Node managers, structured verification, receipt audit, the named validity gate,
and Markdown reporting.

The next run should publish and exercise hosted CI if Sam supplies the remote.
If that remains blocked, benchmark exact Git fingerprinting with many and large
untracked files and optimize the measured bottleneck without weakening drift
detection.

## 2026-08-14 — Faster exact Git state inspection

Continued ProofRun after a full repository, history, documentation, test, and
active-message review. Sam's GitHub remote handoff remains unanswered, so the
run completed the documented local performance task. A disposable benchmark
with 4,002 untracked files totaling about 50 MB measured the old exact
`git_state` implementation at 0.300 seconds best-of-four warm samples.

The old path independently probed repository availability, head, branch,
tracked paths, untracked paths, and dirty state, causing seven Git subprocesses
even when no tracked file had changed. ProofRun now parses one NUL-delimited
porcelain-v2 status snapshot for all of that metadata and path discovery.
Per-file SHA-256 values and the aggregate fingerprint remain unchanged for
normal filesystem paths. Untracked content is now read in 1 MiB chunks instead
of allocating each complete file, and filesystem path bytes are hashed with
the platform encoding so unusual names are handled safely.

Added regressions proving the untracked-only path uses one Git call and retains
an embedded newline in a filename, plus coverage for staged rename parsing and
detached HEAD. A direct compatibility fixture confirmed identical tracked maps,
untracked maps, and aggregate fingerprints across unstaged edits, staged edits,
renames, and untracked files. The same benchmark reached 0.204 seconds after
the change, a 32% reduction. The suite now has 46 passing tests and ProofRun is
version 1.6.0.

The next run should configure and validate hosted CI if Sam supplies the
remote. Otherwise, it should benchmark repositories with many tracked changes:
exact path-level patch hashing still launches two Git diff subprocesses per
changed path and is now the clearest local fingerprint bottleneck.

## 2026-08-15 — Batched tracked-change fingerprints

Continued ProofRun after inspecting Git state/history, the README, STATUS,
DAILY_LOG, product documentation, tests, implementation, automation memory, and
the active `To-Sam` folder. The optional GitHub remote handoff still has no Sam
reply, so this run completed the documented local performance task rather than
waiting.

A disposable repository with 400 modified tracked files measured the old
fingerprint implementation at 15.443 seconds for one state snapshot. The status
scan was already consolidated, but exact tracked hashing still launched one
working-tree and one staged diff process per path: 801 Git subprocesses total.

ProofRun now retrieves each diff scope as one binary patch plus one NUL-safe
name list, then splits the unchanged patch bytes into per-file blocks before
feeding the existing SHA-256 construction. This reduces the normal snapshot to
five Git calls regardless of the number of changed files while retaining exact
file-level invalidation. If output from an external diff driver or unusual
merge state cannot be paired one block per path, that scope conservatively
falls back to the prior per-path algorithm.

The same 400-file fixture completed in 0.218 seconds best-of-four, about 71
times faster, and its complete tracked digest map matched the legacy result.
Added regression coverage across unstaged, staged, mixed staged/unstaged,
renamed, and embedded-newline paths, including an assertion on the fixed
five-call bound. The suite now has 47 tests and ProofRun is version 1.7.0.

The next run should publish and exercise hosted CI if Sam supplies the remote.
Otherwise, it should exercise generated manifests and verification end to end
in representative disposable Python, Node.js, Rust, and Go projects, then fix
the highest-value adoption failure discovered.

## 2026-08-16 — Mutation-safe Python bootstrap

Continued ProofRun after inspecting Git state and history, all product and
handoff documentation, the implementation, tests, automation memory, and the
active `To-Sam` request. Sam's optional GitHub remote handoff remains
unanswered, so this run followed the documented local adoption path.

Disposable first-run fixtures exercised Python/unittest, Node/npm, Go, and Rust
project detection. Node initialized and verified end to end. Go initialized and
verified after redirecting its host cache into sandbox-writable temporary
storage. Rust detection generated the intended `cargo test` manifest, but Cargo
is not installed on this host. Python exposed two real bootstrap failures: the
generated `python` launcher did not exist on this `python3`-only machine, and a
passing unittest run then created `__pycache__`, causing ProofRun's mutation
guard to reject its own generated check.

Detected Python presets now choose `python3` or `python` from the interpreter
family running ProofRun. They invoke Python with `-B`, and pytest presets also
disable the cache provider, keeping minimal repositories clean without weakening
mutation detection. Added Unix, PyPy, virtualenv, and Windows-style launcher
coverage plus a real init, commit, verify, and clean-worktree regression. The
same external Python fixture now passes verification and the named proof gate.
ProofRun is version 1.7.1 and the suite grew from 47 to 49 tests.

Validation covered the 49-test suite directly and through structured ProofRun
verification, compileall with external bytecode storage, diff checks, JSON init
preview parsing, workflow YAML parsing, receipt-chain audit, the named validity
gate, Markdown reporting, version inspection, and the Python, Node, and Go
adoption gates. The next local task, if the remote is still unavailable, should
redirect detected Rust build output into ignored `.proofrun/` storage and add a
mutation-safe end-to-end regression that can run when Cargo is available.

## 2026-08-17 — Mutation-safe Rust build output

Continued ProofRun after inspecting Git status and history, repository and
automation-memory handoffs, all product documentation, the implementation,
tests, and `To-Sam/`. The second optional request for a GitHub remote remains
unanswered, so local product work continued with the next documented Rust
adoption gap. Cargo is still not installed on this host.

Detected presets can now carry environment overrides into the generated
manifest. The Rust preset sets `CARGO_TARGET_DIR` to
`.proofrun/cargo-target`, which is covered by ProofRun's runtime-local
`.proofrun/.gitignore`. As a result, ordinary Cargo build output cannot cause a
passing generated check to be rejected as a repository mutator merely because
the adopter lacks a root `target/` ignore rule. The exact detected environment
is also present in structured init previews and remains recorded in receipts.

Added an executable adoption regression that creates a Rust-shaped repository,
runs `proofrun init`, commits the scaffold, invokes verification through a
deterministic Cargo stand-in, enforces the named proof gate, inspects the
receipt environment, and confirms the worktree stays clean while the fake
build artifact exists under `.proofrun/cargo-target`. This verifies the whole
ProofRun integration without pretending native Rust compilation ran. Cargo can
still create or update `Cargo.lock`; that file is meaningful verification input
and intentionally remains visible to mutation detection, so adopters should
stabilize it before verification.

ProofRun is version 1.7.2 and the suite grew from 49 to 50 tests. Validation
covered the full suite, compilation, whitespace checks, structured init preview,
workflow YAML parsing, manifest-driven structured verification, receipt audit,
the named validity gate, Markdown reporting, and version output. The next local
task, if hosted CI remains unavailable, should run this fixture with native
Cargo when a runtime becomes available; otherwise add a real pytest adoption
fixture and fix the highest-value failure it exposes.

## 2026-08-18 — Runnable Python CI scaffolds

Continued ProofRun after inspecting Git state and history, automation memory,
all product and handoff documentation, tests, implementation, and `To-Sam/`.
The optional GitHub remote request remains unanswered. Cargo is unavailable,
so this run followed the documented pytest adoption path.

The host interpreter did not include pytest. A disposable `uv` environment
provisioned pytest 9.1.1 and exercised a real pytest-shaped repository through
automatic detection, manifest and workflow creation, commit, verification,
named proof gating, and a clean final Git state. The mutation-safe command
worked as intended: `-B` suppressed bytecode and `-p no:cacheprovider`
suppressed `.pytest_cache`.

The exercise highlighted a larger first-run gap in generated CI: Python
workflows installed ProofRun but did not install pytest or project test
requirements. Detected Python presets now retain the conventional requirements
files present in the repository. Generated workflows install
`requirements.txt`, `requirements-dev.txt`, and `requirements-test.txt` in a
stable order, then explicitly add pytest when that runner was selected. This
setup runs before ProofRun verification, so dependency installation is outside
the repository snapshots that form evidence. Nonstandard dependency managers
and optional extras remain deliberately outside narrow automatic detection.

Added workflow regressions for minimal pytest, all three requirements files,
and unittest with requirements, plus the real pytest init-to-gate fixture. The
dependency-free suite now has 52 tests with the real-runner fixture skipped when
pytest is absent; all 52 execute in the disposable pytest environment. ProofRun
is version 1.8.0. The next local task, if hosted CI and native Cargo remain
unavailable, should exercise pnpm, Yarn, and Bun generated workflows end to end
and fix the highest-value failure found.

## 2026-08-19 — Deterministic pnpm setup versions

Continued ProofRun after inspecting Git state and history, automation memory,
the README, STATUS, DAILY_LOG, product documentation, tests, implementation,
and the active `To-Sam/` request. Sam's optional GitHub remote handoff remains
unanswered, so the run followed the documented local Node adoption path.

Native pnpm and Yarn probes reached the installed Corepack runtime but could not
download their package managers because the host registry certificate chain was
not accepted. The installed Bun runtime remained available. Current official
pnpm action documentation and active upstream v6 regressions exposed a concrete
generated-workflow risk: ProofRun omitted `with.version` when `packageManager`
declared pnpm, leaving the setup action to infer a version even though v6 has
been reported selecting a different release.

Detected Node presets now parse and retain the declared package-manager version,
remove the optional Corepack integrity suffix only for the setup-action input,
and reject malformed declarations that do not use `manager@version`. Generated
pnpm workflows pass that version explicitly; lockfile-only projects still use
the explicit `latest` fallback because their repository contains no
authoritative tool version. Structured dry-run JSON now exposes the parsed
version for agent review.

Added regressions for version retention, integrity suffixes, malformed
declarations, generated workflow input, and structured previews. ProofRun is
version 1.8.1 and the suite has 53 tests. The next local task, if hosted CI and
native Cargo remain unavailable, should complete native pnpm/Yarn fixtures when
the certificate path is repaired, or add a real Bun init-to-proof fixture using
the installed runtime.

## 2026-08-20 — Product lab pivot prepared

Sam confirmed that ProofRun's local MVP can be treated as complete and explicitly
requested a switch to a new idea. The repository was reorganized so this intent
survives without conversational memory: all ProofRun-specific source, tests,
packaging, documentation, and its example workflow now live under
`products/proofrun/`.

Root `README.md` and `STATUS.md` now describe a multi-product lab rather than an
active ProofRun project. `NEXT_RUN.md` requires the next autonomous run to
research at least three current opportunities, compare them, select one, rename
the `products/next-product/` placeholder to a stable product slug, and build a
tested runnable wedge in the same run. The optional ProofRun remote request was
archived because distribution work is no longer the active objective.

ProofRun v1.8.1 remains frozen and recoverable with its original documentation
and history. Its 53-test suite and manifest-driven verification were rerun from
the nested product directory after the move. The next run should begin with
fresh opportunity evidence rather than extending ProofRun or automatically
reviving the candidates from its original exploration.

## 2026-08-20 — AgentScope v0.1.0 selected and built

Followed the documented product pivot after inspecting the clean Git state and
recent history, automation memory, root and product handoffs, ProofRun source
and tests, and `To-Sam/`. No active Sam message was present. The frozen ProofRun
baseline remained healthy: all 53 tests passed with one expected skip because
the optional real pytest runtime is not installed.

Researched three current opportunities: an instruction-scope debugger, an MCP
configuration change reviewer, and a coding-agent environment preflight. The
comparison used the open AGENTS.md format, current GitHub Copilot instruction
and environment documentation, current VS Code and MCP security guidance, and
visible adjacent open-source tools. Instruction scope was selected because
clients now combine several formats under differing scope rules, while existing
linters primarily validate content, references, or general readiness rather
than answering which guidance applies to one target under a named client model.
The evidence and risks are preserved in
`products/agentscope/docs/OPPORTUNITIES.md`.

Replaced the temporary `products/next-product/` workspace with AgentScope
v0.1.0. The dependency-free Python CLI accepts existing or planned target paths,
rejects repository escapes, and models both nearest-file `AGENTS.md` precedence
and Copilot CLI aggregation. It explains applied, shadowed, and ignored sources;
evaluates conservative scalar `applyTo` globs; emits stable schema-v1 JSON; and
can exit nonzero when any target lacks applicable guidance. Product-local
instructions make the tool immediately dogfoodable.

Seven automated tests cover nested precedence, planned files, cross-format
aggregation, matching and nonmatching path rules, one-segment glob behavior,
repository containment, JSON, gate exits, and invalid roots. Direct tests,
compileall, human/JSON smoke runs, package metadata parsing, whitespace checks,
and the preserved ProofRun suite passed. The next run should add a cross-profile
comparison and divergence gate before widening instruction syntax support.

## 2026-08-20 — AgentScope cross-profile comparison

Continued AgentScope after inspecting the automation memory, clean Git state and
history, portfolio handoffs, active messages, product documentation, tests, and
implementation. The existing seven-test baseline passed and no active message
from Sam required a change in direction.

AgentScope v0.2.0 adds a comparison model separate from presentation. For every
requested target, it evaluates both supported profiles and preserves their
ordered applied paths, the paths common to both, and the paths unique to each.
Only effective applied-path differences count as divergence, so a discovered
but unmatched Copilot path rule does not create a false policy failure.

The new `agentscope compare TARGET...` surface renders concise human groups or a
schema-v1 JSON document with aggregate divergence counts and per-profile source
sets. Informational comparisons still exit 0; `--fail-on-divergence` exits 1
when any target differs, while invalid repository input retains exit 2. Existing
inspection syntax and its missing-guidance gate remain unchanged.

Five new tests cover nested `AGENTS.md`, Copilot-only `CLAUDE.md`, matching and
unmatched path rules, multiple targets, empty guidance, human output, JSON, and
the gate contract. The full 12-test AgentScope suite, compilation, JSON parsing,
human dogfooding, package metadata, whitespace checks, and the frozen ProofRun
baseline passed. The next run should build a source-grounded compatibility
matrix for scalar `applyTo` globs and align the matcher with documented GitHub
semantics before adding broader frontmatter or `@` reference support.

## 2026-08-21 — AgentScope dot-path glob compatibility

Continued AgentScope after inspecting the clean Git state and history,
automation memory, portfolio handoffs, active `To-Sam/` messages, product
documentation, tests, and implementation. No Sam request was active, and the
12-test AgentScope baseline passed before changes.

GitHub's current Copilot CLI documentation now provides a concrete glob example
set for root-only wildcards, recursive wildcards, anchored directories, nested
segments, and comma-separated patterns. Those examples are captured in a new
source-linked compatibility matrix and an executable table, along with explicit
AgentScope boundaries for `?`, dot paths, `./`, and undocumented leading `/`.

The matrix exposed a real normalization defect: `lstrip("./")` removed every
leading dot or slash character rather than one optional `./` prefix. As a
result, `.github/**/*.yml` could not match `.github/workflows/test.yml`, `.*`
incorrectly matched ordinary root files, and `/src/*.py` silently behaved like
`src/*.py`. Normalization now removes exactly one explicit `./`, preserving all
other leading path characters.

Added 26 table rows and an end-to-end comma-separated OR regression, taking the
suite from 12 to 14 tests and AgentScope to v0.2.1. Both schema-v1 JSON surfaces,
both policy gates, compilation, package metadata, and representative existing
and planned targets passed. Frozen ProofRun also passed all 53 tests with one
expected optional pytest-runtime skip; its 49-receipt chain remains audit-valid.
The next run should explain supported Copilot CLI `@` references with cycle,
depth, missing-file, and repository-escape diagnostics.

## 2026-08-22 — AgentScope recursive instruction references

Continued AgentScope after inspecting the clean Git state and recent history,
automation memory, portfolio and product handoffs, active `To-Sam/` messages,
documentation, implementation, and tests. No Sam request was active, and the
14-test v0.2.1 baseline passed before changes.

GitHub's current Copilot CLI documentation confirms that repository Copilot
instructions, `AGENTS.md`, and `CLAUDE.md` can import relative `@path` files
recursively. Referenced files must remain in the repository; absolute and
home-relative paths are not loaded; and imports are not expanded from
`GEMINI.md` or modular `*.instructions.md`. GitHub documents cycle, size, and
depth guards without publishing their numeric limits.

AgentScope v0.3.0 now resolves supported imports immediately and depth-first,
relative to each containing file. Valid files appear as applied
`copilot-reference` sources, are deduplicated after their first appearance, and
participate in cross-profile divergence. Missing or non-file targets, cycles,
absolute and `~/` paths, repository and symlink escapes, and excess depth appear
as ordered `invalid` diagnostics and do not increase applied counts. AgentScope
uses an explicit 10-edge safety limit, documented as its own conservative
boundary rather than Copilot CLI's unpublished value. `GEMINI.md` and path-
specific sources preserve their existing no-expansion behavior.

The existing source object accommodates the new kind and state, so both human
output and inspection schema v1 remain structurally stable. Added a source-
linked reference contract and six end-to-end tests for recursive relative
imports, comparison, cycles, missing and disallowed paths, source boundaries,
depth, symlink escapes, and human/JSON rendering. The AgentScope suite grew from
14 to 20 tests;
tests, compilation, version/TOML checks, JSON parsing, human comparison, and
diff checks passed. Frozen ProofRun passed all 53 tests with one expected
optional pytest skip, and its receipt chain is audit-valid.

The next run should add an opt-in invalid-reference policy gate and aggregate
diagnostic counts for human and JSON consumers while keeping ordinary
inspection informational.

## 2026-08-23 — AgentScope enforceable reference diagnostics

Continued AgentScope after inspecting the clean Git state and recent history,
automation memory, portfolio handoffs, active `To-Sam/` messages, all active
product documentation, implementation, and tests. No Sam request was active,
and the 20-test v0.3.0 baseline passed before changes.

AgentScope v0.4.0 adds `--fail-on-invalid-references` as an opt-in inspection
policy. Ordinary inspection remains informational and exits 0; the gate exits 1
after rendering the full report when any selected target has a rejected
Copilot reference. Invalid repository input retains exit 2. The new policy and
`--require-instructions` compose with OR semantics across multiple targets, so
either missing guidance or an invalid reference is enforceable without losing
the other targets' diagnostics. The reference gate is inert for profiles that
do not model reference diagnostics.

Human inspection now summarizes applied-source and invalid-reference totals and
adds the diagnostic count to every target heading while retaining the ordered
source-level reasons. Inspection JSON moved from schema v1 to v2 with additive
`invalid_reference_count` fields at the document and target levels. Aggregate
counts sum per-target occurrences, which preserves the impact of a shared bad
source across several requested targets. The existing source objects are
unchanged, and comparison JSON remains schema v1 because its shape did not
change.

The AgentScope suite grew from 20 to 21 tests with coverage for the default,
both gates independently and together, multi-target aggregation, profile
boundaries, human/JSON output, and invalid-input precedence. Tests, compilation,
CLI help/version, package metadata, schema parsing, dogfooding, and whitespace
checks passed. Frozen ProofRun passed all 53 tests with one expected optional
pytest-runtime skip; its 52-receipt chain remains audit-valid.

The next run should distinguish malformed or unsupported path-instruction
frontmatter from a valid nonmatching rule, then evaluate a broader invalid-source
policy without silently widening the reference-specific gate.

## 2026-08-24 — AgentScope path-instruction diagnostics

Continued AgentScope after inspecting the clean Git state and recent history,
automation memory, portfolio handoffs, active `To-Sam/` messages, every active
product document, implementation, and test. No Sam request was active, and the
21-test v0.4.0 baseline passed before changes. Frozen ProofRun remained outside
the active implementation scope.

GitHub's current Copilot CLI documentation requires a frontmatter block at the
start of each `*.instructions.md` file, demonstrates `applyTo` as a one-line glob
scalar, and separates multiple patterns with commas. It documents
`excludeAgent` as an optional sibling key but does not publish list, mapping, or
multiline `applyTo` forms. AgentScope now implements that narrow contract
directly without adding a YAML runtime dependency.

AgentScope v0.5.0 distinguishes invalid configuration from a valid scope miss.
Missing opening or closing delimiters, missing or duplicate keys, empty values,
block and inline lists, mappings, multiline values, missing colons, unmatched
quotes, and empty comma items produce precise ordered `invalid` path sources.
Valid scalar globs retain all v0.2.1 matching behavior; a valid nonmatch remains
`ignored`. The source object shape and recursive-reference behavior are
unchanged.

Inspection JSON moved from schema v2 to v3 with additive aggregate and
per-target `invalid_source_count` values. The existing
`invalid_reference_count` remains its narrower subset. A new opt-in
`--fail-on-invalid-sources` gate enforces the superset while the existing
reference gate keeps its exact behavior; all inspection gates compose with OR
semantics, render before failing, remain informational by default, and preserve
exit 2 for invalid repository input. Comparison remains schema v1 and compares
applied paths only.

Added a source-linked frontmatter compatibility contract and two test methods,
bringing the suite from 21 to 23 tests. Validation covered Python 3.14 and
warning-strict Python 3.11 suites, compilation, human and both JSON surfaces,
policy exits, a Python 3.11 wheel build/install smoke, package metadata,
whitespace checks, and the frozen ProofRun test and evidence baseline. The next
run should align remaining repository-local Copilot discovery with current
documentation, beginning with `.claude/CLAUDE.md`, before considering user-level
instruction inputs.

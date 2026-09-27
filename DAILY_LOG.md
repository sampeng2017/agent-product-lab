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

## 2026-08-25 — AgentScope nested repository discovery

Continued AgentScope after inspecting the clean Git state and history,
automation memory, portfolio handoffs, active `To-Sam/` messages, every active
product document, implementation, and test. No Sam request was active, and the
23-test v0.5.0 baseline passed before changes. Frozen ProofRun remained outside
the active implementation scope.

GitHub's current Copilot CLI documentation defines repository and agent
instruction discovery across standard locations, explicitly includes
`.claude/CLAUDE.md`, says applicable sources are combined without a general
precedence order, and removes duplicate copies. AgentScope now models the
selected repository root and each target ancestor as its explicit
standard-location chain. It discovers nested `.github/copilot-instructions.md`,
`AGENTS.md`, `CLAUDE.md`, `.claude/CLAUDE.md`, `GEMINI.md`, and ancestor
`.github/instructions/**/*.instructions.md` trees.

AgentScope v0.6.0 presents standard files root-to-target in a documented
per-directory order, expands supported imports immediately in depth-first
order, and then presents modular sources root-to-target with stable path
sorting. This is an AgentScope reporting contract rather than a precedence
claim. Direct and referenced routes now share a resolved-path discovery set, so
the first route wins and later standard, modular, or equivalent symlink routes
do not duplicate a source.

Added a source-linked discovery compatibility contract and two end-to-end test
methods for nested locations, ordering, matching, and cross-route
deduplication. The suite grew from 23 to 25 tests while inspection schema v3,
comparison schema v1, source objects, reference/frontmatter diagnostics, and
policy exits remained unchanged. Python 3.14 and warning-strict Python 3.11
tests, compilation, human/JSON dogfooding, metadata parsing, and diff checks
passed, as did an isolated Python 3.11 wheel build/install and console smoke.
Frozen ProofRun passed all 53 tests with one expected optional pytest skip, and
its 54-receipt chain remained audit-valid. The next run should add an explicit
repository-contained Copilot session-directory input and distinguish
intermediate-only directories from target-nested locations for modular
discovery.

## 2026-08-26 — AgentScope explicit session discovery

Continued AgentScope after inspecting the clean Git state and recent history,
automation memory, portfolio and product handoffs, active `To-Sam/` messages,
all active-product documentation, implementation, and tests. No Sam request was
active, and the 25-test v0.6.0 baseline passed before changes. Frozen ProofRun
remained outside the active implementation scope.

Rechecked GitHub's current Copilot CLI custom-instruction documentation. It
still defines ordinary standard locations at the repository root, session
working directory, directories between them, and target-nested directories,
while explicitly excluding modular `*.instructions.md` discovery from
intermediate directories.

AgentScope v0.7.0 adds `--cwd` to inspection and comparison as explicit model
input. Relative values are anchored at `--root`; absolute values must still be
contained. The directory must exist, be a directory, and remain within the
repository after symlink resolution. AgentScope does not change the process
working directory or infer hidden process state, and the repository-root
default preserves v0.6.0 behavior.

The Copilot profile now classifies standard discovery as repository root,
session intermediate, session, and target-nested locations. Standard files use
all four roles; modular instruction trees use root, session, and target-only
locations but skip intermediate-only directories. Divergent session and target
branches are deterministic: the session branch is reported before the target
branch. Planned targets remain supported, source reasons expose the location
role, and resolved-path/reference deduplication remains first-route-wins.

Inspection schema v4 and comparison schema v2 add the repository-relative
`session_directory` so saved results remain reproducible; existing target and
source object shapes and gate exits are unchanged. Four test methods cover
nested and divergent sessions, planned targets, root-default compatibility,
outside/file/symlink containment, role reasons, and both CLI JSON contracts,
expanding the suite from 25 to 29 tests.

AgentScope passed all 29 tests under Python 3.14 and warning-strict Python 3.11,
plus compilation and whitespace checks. Frozen ProofRun passed all 53 tests
with one expected optional pytest skip. Package/CLI and post-commit evidence
validation are recorded in the final run handoff. The next run should add
explainable identical-content deduplication for eligible Copilot standard files
without disturbing session-aware ordering or resolved-path deduplication.

## 2026-08-28 — AgentScope standard-content deduplication

Continued AgentScope after inspecting the clean Git state and history,
automation memory, portfolio handoffs, active `To-Sam/` messages, all active
product documentation, implementation, and tests. No Sam request was active,
and the 29-test v0.7.0 baseline passed before changes. ProofRun remained frozen.

Rechecked GitHub's current Copilot CLI custom-instruction documentation. It
still says Copilot combines applicable sources while removing duplicate copies
of identical user-level, repository-wide, and agent instructions; modular
path-specific files remain a separate matching category. The same page says
line placement and blank lines do not affect instruction content.

AgentScope v0.8.0 now compares normalized complete text across the modeled
standard files: `.github/copilot-instructions.md`, `AGENTS.md`, both `CLAUDE.md`
locations, and `GEMINI.md`. It removes blank lines, trims surrounding line
whitespace, and joins nonblank lines with spaces. The first source remains
`applied`; later distinct paths with the same value appear as `duplicate` and
name the retained source. Partial-content similarity never deduplicates.

Resolved-path and symlink identity still win before content comparison.
Modular and imported files neither participate in nor seed the standard-content
map. Duplicate wrappers still expand supported `@` lines immediately from their
own locations, so identical wrapper text cannot hide distinct relative imports.
Comparison continues to use applied paths only. The existing source object
already carries state and reason, so inspection schema v4 and comparison schema
v2 remain unchanged.

Two new test methods cover root, intermediate, session, target-nested, and
divergent discovery; cross-kind and whitespace-normalized copies; distinct
partial content; modular exclusions; retained-source reasons; human/JSON state;
and copied wrappers with different relative imports. The suite grew from 29 to
31 tests and passed under Python 3.14 and warning-strict Python 3.11. Compilation,
version/TOML checks, inspection and comparison JSON dogfooding, whitespace
checks, and an isolated Python 3.11 wheel build/install smoke passed. Frozen
ProofRun passed all 53 tests with one expected optional pytest-runtime skip.

The next run should evaluate a repeatable, repository-contained CLI input for
additional Copilot instruction directories without implicitly reading
`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` from the process environment.

## 2026-08-28 — AgentScope explicit additional instruction directories

Continued AgentScope after inspecting the clean Git state and history,
automation memory, portfolio and product handoffs, active `To-Sam/` messages,
all active documentation, implementation, and tests. No Sam request was active,
and the 31-test v0.8.0 baseline passed before changes. ProofRun remained frozen.

Rechecked GitHub's current Copilot CLI documentation. It identifies
`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` as a comma-separated list of directories
that add `AGENTS.md` and `*.instructions.md` sources, but it does not define
their precedence or nested `AGENTS.md` scope. AgentScope v0.9.0 therefore adds a
repeatable `--instructions-dir` model input to inspection and comparison instead
of reading environment state. Relative paths use `--root`; every directory must
exist, resolve inside the repository, and remain contained through symlinks.
Equivalent inputs collapse to their first position.

Ordinary repository/session sources remain first. Each additional directory is
then visited in caller order, contributing its direct `AGENTS.md` followed by
recursively discovered `*.instructions.md` files in path order. This explicit
direct-file boundary avoids inventing nested-agent scope. Additional sources use
the existing recursive-reference, repository-relative glob, normalized-content,
resolved-route, planned-target, comparison, diagnostic, and policy behavior.
Instruction-file symlinks that escape the root now become invalid diagnostics
instead of causing external reads across both ordinary and additional routes.

Inspection schema v5 and comparison schema v3 record the effective deduplicated
`additional_instruction_directories` list while leaving target and source
objects unchanged. Human output records the same context. Three new test
methods cover ordered multiple directories, recursive modular files, imports,
content and route deduplication, planned targets, profile comparison, invalid
policy exits, duplicate inputs, missing/file/outside/symlink directories, and
escaping source symlinks. The suite grew from 31 to 34 tests.

AgentScope passed all 34 tests on Python 3.14 and warning-strict Python 3.11,
plus compilation, metadata, help, human/JSON dogfooding, and diff checks. A
Python 3.11 no-isolation wheel build and isolated console-script install passed.
Frozen ProofRun passed all 53 tests with one expected optional pytest-runtime
skip. Post-commit evidence validation is recorded in the final handoff. The next
run should add a read-only root CI workflow that validates both products and
isolated package installs from one maintained entry point.

## 2026-08-29 — Portfolio compatibility and package CI

Continued AgentScope after inspecting the clean Git state and history,
automation memory, portfolio and product handoffs, active `To-Sam/` messages,
product documentation, implementation, and tests. No Sam request was active.
The AgentScope baseline passed all 34 tests; frozen ProofRun passed all 53 tests
with one expected optional pytest-runtime skip.

Added a root GitHub Actions workflow for push, pull request, and manual runs.
The matrix covers Python 3.10, 3.11, 3.12, 3.13, and 3.14, matching both
packages' `>=3.10` metadata across current stable minors. Python 3.10 promotes
warnings to errors. The workflow uses the current official checkout and Python
setup action majors, grants only read access to repository contents, disables
persisted checkout credentials, fails matrix jobs independently, and has a
bounded timeout. Each job explicitly installs the packages' shared declared
`setuptools>=68` build backend because modern Python installations need not
bundle it.

Added `scripts/validate-portfolio.sh` as the shared local and hosted validation
entry point. For each product it runs the unit suite without checkout bytecode,
compiles sources into a temporary cache, builds a wheel without publishing,
installs the exact wheel with dependencies disabled into a fresh virtual
environment, and exercises the installed console command. All generated state
lives under a temporary directory and is removed on exit. This proves both the
active AgentScope package and frozen ProofRun distribution while keeping the
checkout clean and avoiding editable-install blind spots. The validator
preflights the build backend and emits a concise remediation when a selected
local interpreter does not provide it.

Updated root and AgentScope documentation, product status, and the next-run
handoff. Final validation passed through the warning-strict shared script on
Python 3.11: all 34 AgentScope tests, 52 ProofRun tests with one expected skip,
both compile passes, both no-isolation wheel builds, both isolated installs, and
both console smokes. Shell syntax, dependency-free Ruby YAML parsing, Git
whitespace checks, the missing-backend preflight, and checkout cleanliness also
passed. The next run should make unreadable or non-UTF-8 Copilot standard files
explicit invalid diagnostics so `--fail-on-invalid-sources` cannot accept
instructions AgentScope could not inspect.

## 2026-08-30 — AgentScope unreadable-source diagnostics

Continued AgentScope after inspecting the clean Git state and history,
automation memory, root and product handoffs, active `To-Sam/` messages, all
AgentScope documentation, implementation, and tests. No Sam request was active,
the 34-test v0.9.0 baseline passed, and ProofRun remained frozen.

AgentScope v0.10.0 now requires every directly discovered Copilot source to be
readable UTF-8 before it is applied, normalized for duplicate detection, or
used for reference expansion. Invalid encoding produces the stable diagnostic
`instruction file is not valid UTF-8`; other read failures produce
`instruction file could not be read`. Neither outcome includes exception text
or instruction content, both use the existing `invalid` state, and apparent
references in unreadable content are not partially expanded.

Referenced files now receive the same validation before they are marked
applied. An unreadable import is an invalid `copilot-reference`, names its
referring path, stops recursion at that edge, contributes to both invalid-source
and invalid-reference counts, and is enforceable through either applicable
inspection gate. Modular read failures use the same two stable categories.
Valid-source discovery order, path/content deduplication, matching, and output
remain unchanged.

The existing source objects, invalid counts, and `invalid` state already express
the new behavior, so inspection schema v5 and comparison schema v3 remain
stable. Comparison continues to retain applied paths only; an unreadable shared
`AGENTS.md` can therefore appear as divergence, but the reason is not preserved.
That limitation is the next recommended improvement.

Added three end-to-end test methods for invalid byte sequences, a portably
simulated `OSError`, privacy-safe diagnostics, safe reference stopping, human
and JSON output, broad and narrow policy exits, comparison behavior, and
unaffected valid sources. The focused suite grew from 34 to 37 tests and passed
with compilation, version, and whitespace checks. The warning-strict Python
3.11 portfolio validator passed all 37 AgentScope tests and all 53 frozen
ProofRun tests with one expected optional pytest skip, then built, isolated-
installed, and smoke-tested both wheels. The default Python 3.14 interpreter's
expected missing-build-backend preflight was also confirmed before selecting
the established Python 3.11 validation path. No human input is needed.

## 2026-09-01 — AgentScope comparison invalid-source evidence

Continued AgentScope after inspecting the clean Git state and history,
automation memory, root and product handoffs, active `To-Sam/` messages, all
AgentScope documentation, implementation, and tests. No Sam request was active,
the 37-test v0.10.0 baseline passed, and ProofRun remained frozen.

AgentScope v0.11.0 now preserves each profile's ordered invalid sources in
comparison results instead of reducing each inspection to applied paths alone.
Direct-library results expose invalid-source and invalid-reference counts per
profile and target. Human output adds the counts and ordered diagnostics;
schema-v4 JSON adds the same aggregates plus complete source objects, including
path, kind, state, reason, and patterns where applicable. The new field on the
profile comparison dataclass has an empty default to preserve practical
three-argument construction compatibility.

Added `agentscope compare --fail-on-invalid-sources`. It renders the full human
or JSON report before returning exit 1 and composes with
`--fail-on-divergence` using OR semantics. Divergence remains defined only by
profile-specific applied paths: malformed, unreadable, or invalid-reference
sources are reported separately and cannot turn an otherwise consistent source
set into false divergence.

Expanded the focused suite from 37 to 39 tests. Coverage now includes ordered
invalid evidence, malformed modular instructions, invalid references,
unreadable standard files, consistent-invalid and divergent-invalid results,
human and JSON output, schema-v4 aggregates, and both comparison policies.
Focused tests, compilation, metadata, JSON dogfooding, and whitespace checks
passed. The warning-strict Python 3.11 portfolio validator passed all 39
AgentScope tests and all 53 frozen ProofRun tests with one expected optional
pytest-runtime skip, then built, isolated-installed, and smoke-tested both
wheels. No human input is needed. The next run should add the narrower
`compare --fail-on-invalid-references` policy already available to inspection.

## 2026-09-02 — AgentScope narrow comparison reference policy

Continued AgentScope after inspecting the clean Git state and history,
automation memory, root and product handoffs, active `To-Sam/` messages, all
AgentScope documentation, implementation, and tests. No Sam request was active,
the 39-test v0.11.0 baseline passed, and ProofRun remained frozen.

AgentScope v0.12.0 adds `compare --fail-on-invalid-references`, bringing the
narrow broken-import policy already available during inspection to profile
comparison. The gate evaluates the comparison schema-v4 invalid-reference
counts across every target and profile. It returns exit 1 only after the full
human or JSON report is rendered and composes with `--fail-on-divergence` and
`--fail-on-invalid-sources` using OR semantics. Invalid repository input keeps
exit 2.

The narrow policy deliberately ignores malformed non-reference sources, which
remain enforceable through the broad invalid-source gate. Discovery, ordered
diagnostics, applied-path divergence, direct-library result objects, inspection
schema v5, and comparison schema v4 are unchanged. A focused regression covers
malformed modular instructions, broken imports, two targets, schema totals, and
all three comparison gates together. The suite grew from 39 to 40 tests.

Focused tests, comparison help, version inspection, and whitespace checks
passed. The warning-strict Python 3.11 portfolio validator passed all 40
AgentScope tests and all 53 frozen ProofRun tests with one expected optional
pytest-runtime skip, then built, isolated-installed, and smoke-tested both
wheels. No human input is needed. The next run should define useful
missing-guidance semantics for comparison before deciding whether to add a gate.

## 2026-09-03 — AgentScope comparison guidance requirement

Continued AgentScope after inspecting the clean Git state and recent history,
automation memory, root and product handoffs, active `To-Sam/` messages, all
AgentScope documentation, implementation, and tests. No Sam request was active,
the 40-test v0.12.0 baseline passed with warnings treated as errors, and
ProofRun remained frozen.

Defined missing comparison guidance as a target for which every compared
profile has zero applied sources. AgentScope v0.13.0 adds
`compare --require-instructions` using that union-of-profiles rule: a wholly
uncovered target exits 1, while intentional `agents-md`-only or
`copilot-cli`-only coverage passes unless the caller separately requests
`--fail-on-divergence`. The new gate composes with divergence,
invalid-reference, and invalid-source policies using OR semantics and emits the
complete human or JSON report before failing. Invalid repository input remains
exit 2.

Human comparison output now labels wholly uncovered targets `UNGUIDED` rather
than `CONSISTENT` and includes an aggregate unguided-target count. The public
`TargetComparison.has_applied_guidance` property centralizes that classification.
Inspection schema v5 and comparison schema v4 remain unchanged because each
profile's existing applied-source list already encodes the condition. One new
regression covers one-profile coverage, mixed covered/uncovered target sets,
empty repositories, human and JSON rendering, and informational versus gated
exit behavior; the focused suite grew from 40 to 41 tests.

Warning-strict Python 3.11 portfolio validation passed all 41 AgentScope tests
and all 53 frozen ProofRun tests with one expected optional pytest-runtime skip,
then built, isolated-installed, and smoke-tested AgentScope 0.13.0 and ProofRun
1.8.1 wheels. Focused version, comparison dogfood, help, and whitespace checks
also passed. No human input is needed. The next run should retain ignored,
duplicate, and shadowed source evidence in comparison output so non-applied
profile behavior remains explainable.

## 2026-09-04 — AgentScope non-applied comparison evidence

Continued AgentScope after inspecting the clean Git state and recent history,
automation memory, root and product handoffs, active `To-Sam/` messages, all
AgentScope documentation, implementation, and tests. No Sam request was active,
the 41-test v0.13.0 baseline passed with warnings treated as errors, and
ProofRun remained frozen.

AgentScope v0.14.0 now retains every `ignored`, `duplicate`, and `shadowed`
source in each profile comparison. These source objects preserve inspection
order, path, kind, state, reason, and any `applyTo` patterns. Invalid sources
remain in their separate collection, while applied and profile-unique paths
continue to drive divergence exactly as before. Missing-guidance classification
and all existing policy exit contracts are unchanged.

Human comparison output adds aggregate and per-target non-applied counts plus a
separate per-profile `NON-APPLIED` section with state and explanation.
Comparison JSON advances from schema v4 to v5 and adds
`non_applied_source_count` at document, target, and profile levels plus ordered
`non_applied_sources` arrays per profile. Inspection remains schema v5 because
its complete source objects already represented these states.

One new end-to-end regression plus an expanded unmatched-rule regression cover
matched and ignored modular rules, normalized content duplicates, nested
`AGENTS.md` shadowing, deterministic multi-target order, direct result objects,
human output, and JSON output. The suite grew from 41 to 42 tests. Focused
warning-strict tests, compilation, version inspection, comparison JSON parsing,
and whitespace checks passed. The warning-strict Python 3.11 portfolio
validator passed all 42 AgentScope tests and all 53 frozen ProofRun tests with
one expected optional pytest-runtime skip, then built, isolated-installed, and
smoke-tested AgentScope 0.14.0 and ProofRun 1.8.1 wheels. The default Python
3.14 preflight correctly reported its missing declared build backend before the
established Python 3.11 validation path was selected. No human input is needed.
The next run should evaluate a narrow ignored-path policy without rejecting
intentional duplicates or shadowed ancestors.

## 2026-09-05 — AgentScope ignored-source policy gate

Continued AgentScope after inspecting the clean Git state and recent history,
automation memory, root and product handoffs, active `To-Sam/` messages, all
AgentScope documentation, implementation, and tests. No Sam request was active,
the warning-strict 42-test v0.14.0 baseline passed, and ProofRun remained frozen.

AgentScope v0.15.0 adds `--fail-on-ignored-sources` to both direct inspection and
profile comparison. The policy exits 1 only when a requested target has a
source whose existing state is `ignored`: a readable, valid modular instruction
whose `applyTo` patterns do not match that target. It renders the complete human
or schema-v5 JSON report before failing and composes with all existing gates
using OR semantics. Invalid repository inputs still exit 2.

The implementation exposes composable ignored-source counts on inspection,
profile-comparison, and target-comparison result objects. JSON schema v5 remains
unchanged because ordered inspection sources and comparison non-applied sources
already contain the exact `ignored` evidence. One new end-to-end regression
mixes matched and ignored modular rules, normalized duplicates, ancestor
shadowing, malformed sources, multiple targets, both profiles, full JSON output,
and combined policy exits. The focused suite grew from 42 to 43 tests.

Warning-strict Python 3.11 portfolio validation passed all 43 AgentScope tests
and all 53 frozen ProofRun tests with one expected optional pytest-runtime skip,
then built, isolated-installed, and smoke-tested AgentScope 0.15.0 and ProofRun
1.8.1 wheels. Focused compilation, CLI help inspection, and whitespace checks
also passed. No human input is needed. The next run should evaluate a compact
source-oriented modular coverage view so multi-target ignored-rule failures are
easier to diagnose without changing the existing target-oriented schemas.

## 2026-09-06 — AgentScope modular coverage view

Continued AgentScope after inspecting the clean Git state and recent history,
automation memory, root and product handoffs, active `To-Sam/` messages, all
AgentScope documentation, implementation, and tests. No Sam request was active,
the warning-strict 43-test v0.15.0 baseline passed, and ProofRun remained frozen.

AgentScope v0.16.0 adds `agentscope coverage`, a Copilot-specific source-oriented
view of modular instructions across multiple requested targets. The public
`cover_targets` API groups only `copilot-path` evidence, preserves the first
discovery order of sources and caller order of target occurrences, and maps an
applied modular rule to the clearer coverage state `matched`. Standard sources,
references, normalized-content duplicates, and `agents-md` shadows remain in
the existing inspection and comparison views.

Coverage schema v1 records the ordered requested targets, effective session and
additional-directory context, aggregate matched/ignored/invalid occurrence
counts, source patterns, discovered-target counts, and ordered per-source target
outcomes with reasons. The discovered count is intentionally separate from the
requested target count: a target outside a target-nested modular tree's discovery
route is absent rather than falsely classified as an ignored glob. Human output
expresses the same distinction. Optional `--fail-on-ignored-sources` and
`--fail-on-invalid-sources` gates apply only to modular evidence, render the full
report before exit 1, and retain exit 2 for invalid repository input. Existing
inspection and comparison schema v5 contracts are unchanged.

Two end-to-end regressions cover shared root rules, target-specific discovery,
planned targets, explicit additional directories, malformed frontmatter,
first-discovery ordering, caller target ordering, direct result objects, human
and JSON output, empty repositories, and both policy gates. The focused suite
grew from 43 to 45 tests. Documentation was updated throughout, including two
stale comparison-schema references corrected from v4 to v5.

Warning-strict Python 3.11 portfolio validation passed all 45 AgentScope tests
and all 53 frozen ProofRun tests with one expected optional pytest-runtime skip,
then built, isolated-installed, and smoke-tested AgentScope 0.16.0 and ProofRun
1.8.1 wheels. Focused Python 3.14 tests, compilation, coverage help/version and
JSON parsing, and whitespace checks also passed. No human input is needed. The
next run should dogfood coverage on a larger source/target set before deciding
whether an optional compact table or source/path filters are warranted.

## 2026-09-07 — AgentScope compact coverage matrix

Continued AgentScope after inspecting the clean Git state and recent history,
automation memory, root and product handoffs, active `To-Sam/` messages, all
AgentScope documentation, implementation, and tests. No Sam request was active,
the warning-strict 45-test v0.16.0 baseline passed, and ProofRun remained frozen.

Dogfooding the detailed coverage presentation with mixed root and target-nested
rules showed that one line per discovered source/target occurrence makes the
cross-target pattern difficult to scan. AgentScope v0.17.0 therefore adds
`coverage --compact`, an opt-in human rule-by-target matrix. Its `M`, `I`, `X`,
and `-` cells distinguish matched, ignored, invalid, and not-discovered evidence.
Numbered legends preserve full source paths, `applyTo` patterns, first-discovery
order, full target paths, and caller order; the default view remains the place
for per-occurrence reasons.

Compact and JSON output are mutually exclusive. The feature is presentation-
only: public `cover_targets` results, coverage schema v1, aggregate counts,
discovery semantics, and ignored/invalid policy exits are unchanged. The new
end-to-end regression covers mixed states, target-nested non-discovery, ordering,
policy behavior, output-option validation, and double-digit target labels across
a ten-target fixture. The focused suite grew from 45 to 46 tests.

Warning-strict Python 3.11 portfolio validation passed all 46 AgentScope tests
and all 53 frozen ProofRun tests with one expected optional pytest-runtime skip,
then built, isolated-installed, and smoke-tested AgentScope 0.17.0 and ProofRun
1.8.1 wheels. Focused compact-matrix tests, compilation, help inspection, and
whitespace checks also passed. No human input is needed. The next run should
exercise compact coverage on a real high-cardinality repository and add
deterministic column chunking or filters only if horizontal growth is a proven
problem.

## 2026-09-08 — AgentScope bounded compact coverage

Continued AgentScope after inspecting the clean Git state and recent history,
automation memory, root and product handoffs, active `To-Sam/` messages, and
AgentScope documentation, implementation, and tests. No Sam request was active,
the warning-strict 46-test v0.17.0 baseline passed, and ProofRun remained frozen.

A 25-target exercise demonstrated the concrete scaling issue left by v0.17.0:
the compact matrix's rule rows exceeded 130 columns and grew without a bound.
AgentScope v0.18.0 now renders deterministic consecutive chunks of at most 12
target columns. Each chunk names its global caller-order range and repeats all
rule rows, while the single rule and target legends retain complete paths,
patterns, first-discovery source order, and caller target order. Reports with at
most 12 targets keep their established one-table layout.

This is a presentation-only change. Public `cover_targets` results, coverage
schema v1 JSON, detailed reason-bearing output, matched/ignored/invalid/not-
discovered semantics, aggregate counts, and ignored/invalid policy exits are
unchanged. The existing compact regression now covers 25 targets, verifies
three exact chunks and global labels, and bounds rule rows at 65 characters.
The focused suite remains at 46 tests.

Warning-strict Python 3.11 portfolio validation passed all 46 AgentScope tests
and all 53 frozen ProofRun tests with one expected optional pytest-runtime skip,
then built, isolated-installed, and smoke-tested AgentScope 0.18.0 and ProofRun
1.8.1 wheels. The default Python 3.14 validator preflight correctly reported its
missing declared `setuptools>=68` build backend. Focused chunking, compilation,
and whitespace checks also passed. No human input is needed. The next run should
evaluate a display-only modular-source filter on a source-dense fixture, with
all policy gates continuing to inspect the complete unfiltered result.

## 2026-09-09 — AgentScope display-only source filtering

Continued AgentScope after inspecting the clean Git state and history,
automation memory, root/product handoffs, active `To-Sam/` messages, and all
AgentScope documentation, implementation, and tests. No Sam request was active,
the warning-strict 46-test v0.18.0 baseline passed, and ProofRun remained
frozen.

A source-dense exercise used 14 modular rules split across API and documentation
families, plus malformed guidance, mixed match/ignore outcomes, two requested
targets, and target-nested discovery. The unfiltered matrix and legend contained
twice the rows needed for an API-focused review, demonstrating a concrete need
for a source-path selector.

AgentScope v0.19.0 adds repeatable `coverage --source PATH-GLOB` selectors to
both detailed and compact human output. Selectors reuse the documented
repository-relative `*`, `**`, and `?` matcher, combine with OR semantics, and
retain first-discovery order. Filtered reports show the selected and complete
source counts while the header retains complete matched, ignored, and invalid
totals. A selector matching no source produces an explicit display-filter
message.

Filtering is presentation-only. Ignored and invalid gates still evaluate the
complete unfiltered result, so a hidden malformed rule continues to fail a
requested policy. `--source` is rejected with `--json`, keeping coverage schema
v1 complete and unchanged; the public `cover_targets` API, inspection and
comparison schema v5, discovery semantics, target ordering, detailed reasons,
and 12-target compact chunks are also unchanged. One dense end-to-end regression
expanded the focused suite from 46 to 47 tests.

Warning-strict Python 3.11 portfolio validation passed all 47 AgentScope tests
and all 53 frozen ProofRun tests with one expected optional pytest-runtime skip,
then built, isolated-installed, and smoke-tested AgentScope 0.19.0 and ProofRun
1.8.1 wheels. Focused source-filter testing, compilation, CLI help/version, and
whitespace checks passed. No human input is needed. The next run should evaluate
a display-only occurrence-state selector for quickly isolating ignored or
invalid modular rules while preserving complete-result policy gates.

## 2026-09-10 — AgentScope occurrence-state filtering

Continued AgentScope after inspecting the clean Git state and history,
automation memory, root/product handoffs, active `To-Sam/` messages, and all
AgentScope documentation, implementation, and tests. No Sam request was active,
the warning-strict 47-test v0.19.0 baseline passed, and ProofRun remained frozen.

A mixed fixture with matched, ignored, invalid, and target-nested not-discovered
outcomes confirmed that path filtering alone still left policy diagnosis tied to
prior source knowledge. AgentScope v0.20.0 therefore adds repeatable
`coverage --state STATE` selectors for all four compact-matrix states in both
detailed and compact human output.

Selection occurs at source level: any requested outcome selects a source, after
which all of its occurrences remain visible so mixed-state context and detailed
reasons are not lost. Repeated states use OR semantics, while state and source-
path filter families compose with AND. Reports preserve first-discovery order
and explicitly disclose displayed versus complete scope. Filtering remains
presentation-only; headers and ignored/invalid gates use all evidence, and
`--state` is rejected with JSON so coverage schema v1 remains complete. Public
APIs, discovery behavior, inspection/comparison schema v5, compact chunks, and
existing exits are unchanged. One end-to-end regression expanded the suite from
47 to 48 tests.

Warning-strict Python 3.11 portfolio validation passed all 48 AgentScope tests
and all 53 frozen ProofRun tests with one expected optional pytest-runtime skip,
then built, isolated-installed, and smoke-tested AgentScope 0.20.0 and ProofRun
1.8.1 wheels. Focused tests, compilation, help inspection, and whitespace checks
passed. Post-commit ProofRun receipt #68 is valid; the chain contains 62 valid
sealed and 6 legacy unsealed receipts, and named `unit` evidence applies. No
human input is needed. The next run should audit the installed v0.20.0 wheel,
help, docs, and all command surfaces for release readiness; if no concrete
product gap remains, freeze AgentScope and select the next opportunity.

## 2026-09-11 — AgentScope v1.0.0 release audit and freeze

Continued AgentScope after inspecting the clean Git state and history,
automation memory, root/product handoffs, active `To-Sam/` messages, all product
documentation, package metadata, implementation, tests, and the existing
portfolio validator. No Sam request was active. The warning-strict Python 3.11
baseline passed all 48 AgentScope and 53 frozen ProofRun tests with one expected
optional skip, built both wheels, and installed them in fresh environments.

The release audit inspected AgentScope's wheel contents and installed metadata,
all three help surfaces, version reporting, documentation links, and existing
human/JSON/policy tests. No behavior or schema defect remained, but the audit
found that portfolio CI exercised only the installed `agentscope --version`;
meaningful packaged commands could regress while source tests still passed.

Portfolio validation now uses a checked-in realistic repository fixture with
shared and profile-only standard instructions plus matching, ignored, and
malformed modular rules. After isolated wheel installation it runs inspection,
comparison, and coverage in human mode, then checks schema-v5 inspection,
schema-v5 comparison, and schema-v1 coverage JSON policy failures. It requires
exact exit 1 behavior and asserts representative target, divergence, match,
ignore, invalid, and schema counts. The enhanced validator passes end to end.

With no product defect or release blocker left, AgentScope was promoted from
v0.20.0 to v1.0.0 and frozen as the portfolio's second local MVP. Product and
root docs now record its maintenance boundary and stronger artifact validation.
Current packaging and adjacent-tool evidence was compared for four possible
follow-ons. An installed-artifact behavior contract runner was selected over a
wheel-content linter, metadata/README checker, and general environment runner;
those broader jobs are already covered by `check-wheel-contents`, `twine check`,
and tox. The next run should extract the proven AgentScope audit into the
smallest standalone TOML-driven prototype and retain it only if it is materially
clearer than the equivalent shell. No human input is needed.

## 2026-09-12 — WheelContract v0.1.0 prototype

Started the selected third-product opportunity after inspecting the clean Git
state and history, automation memory, all root/product handoffs, active
`To-Sam/` messages, the AgentScope release fixture, and the existing bespoke
artifact audit. No Sam request was active. The warning-strict Python 3.11
baseline passed 48 AgentScope and 53 ProofRun tests with one expected optional
skip, built both wheels, isolated-installed them, and passed the six installed
AgentScope surfaces.

Built WheelContract v0.1.0, a zero-runtime-dependency installed Python CLI wheel
behavior runner. Schema-v1 TOML names one local project or prebuilt wheel and
ordered cases with explicit installed entry-point argument vectors, expected
exits, bounded stdout fragments, and top-level scalar JSON expectations. The
runner builds when needed, installs without dependencies in a disposable virtual
environment, runs outside the checkout with Python import-leak variables
removed, applies per-case time and output bounds, reports every result, and
distinguishes behavior failures (exit 1) from contract/setup failures (exit 2).
Python 3.10 uses a focused fallback parser for the documented schema.

Six focused tests use a real minimal wheel to cover successful text/JSON/exit
contracts, aggregate failures, output bounds, strict and safe command parsing,
missing installed commands, and Python 3.10 fallback behavior. The checked-in
`wheelcontract.toml` then passed all six human, JSON, and policy-exit cases
against a newly built AgentScope wheel.

The portfolio validator now tests, builds, and isolated-installs WheelContract,
then uses its installed command with the already-built AgentScope artifact. This
removed 67 lines of one-off shell and embedded Python assertion logic in favor
of a three-line reusable invocation and a 52-line expectation-adjacent contract.
That is a material clarity and diagnostic reuse improvement, so the product
hypothesis is retained. Warning-strict portfolio validation passed all 6
WheelContract, 48 AgentScope, and 53 ProofRun tests (one expected skip), all
three wheel builds and isolated installs, console smokes, and the six-case
installed artifact contract. No human input is needed. Next, deliberately
exercise failure diagnostics and add structured runner output only if the
dogfood shows a concrete gap.

## 2026-09-13 — WheelContract v0.2.0 stderr and self-contract

Continued WheelContract after inspecting the clean Git state and history,
automation memory, root/product handoffs, active `To-Sam/` messages, product
implementation and tests, both frozen products, and portfolio validation. No
Sam request was active, and the warning-strict Python 3.11 baseline passed all
6 WheelContract, 48 AgentScope, and 53 ProofRun tests with one expected skip.

A copied AgentScope contract then deliberately introduced a missing human text
fragment, a wrong expected exit, and a wrong top-level JSON value while retaining
a passing control. The existing report named all four cases, gave exact actual
and expected values, showed bounded output previews, and returned aggregate exit
1. That was sufficient for source-free CI diagnosis, so no structured runner
output or new output schema was added. The suite now pins those details.

The prescribed second-artifact contract exposed one concrete assumption from
the AgentScope origin: WheelContract could assert stdout but not stable stderr
diagnostics. Version 0.2.0 adds symmetric `stderr_contains` arrays within schema
version 1. A new compact self-contract verifies the installed version, a
missing-contract exit-2 stderr diagnostic, and help output. Portfolio validation
now runs this contract against the built WheelContract wheel before using the
same installed runner for the six-case AgentScope contract.

Warning-strict Python 3.11 portfolio validation passed all 6 WheelContract, 48
AgentScope, and 53 ProofRun tests with one expected skip; all wheels built and
isolated-installed, both contracts passed, and compilation, shell syntax, and
diff checks were clean. The next run should probe timeout behavior with a
child-spawning installed command and add process-tree cleanup only if a real
descendant lifecycle problem is reproduced.

## 2026-09-14 — WheelContract v0.3.0 process-tree cleanup

Continued WheelContract after inspecting the clean Git state and history,
automation memory, root/product handoffs, active `To-Sam/` messages, the full
implementation and test surface, both contracts, and portfolio validation. No
Sam request was active. The warning-strict Python 3.11 baseline passed all 6
WheelContract, 48 AgentScope, and 53 ProofRun tests with one expected skip.

A new disposable installed-wheel case spawned a delayed child and then exceeded
its one-second timeout. The existing `subprocess.run` behavior killed only the
direct command: the descendant survived the contract and wrote its marker. This
reproduced the lifecycle gap before implementation changed.

WheelContract v0.3.0 now starts every case in an isolated process group. A Unix
timeout sends graceful termination to the group, retains the leader through a
fixed half-second grace so the group identifier cannot be recycled, force-kills
residual descendants, and reaps the direct child with bounded waits. Windows
starts a new process group and invokes native `/T /F` tree termination with a
five-second bound plus direct-process fallback. The end-to-end regression uses
a child that ignores graceful termination and confirms it cannot write after the
contract returns; a separate mock-backed test pins the Windows invocation. No
manifest, schema, CLI, diagnostic, or exit-code surface changed.

Final warning-strict Python 3.11 portfolio validation passed all 8 WheelContract,
48 AgentScope, and 53 ProofRun tests with one expected skip. All three wheels
built and isolated-installed, the three-case WheelContract self-contract and
six-case AgentScope contract passed, and compilation and diff checks were clean.
No human input is needed. The next run should perform a release-readiness audit
and promote/freeze WheelContract only if no concrete blocker remains.

## 2026-09-15 — WheelContract v1.0.0 release freeze

Continued WheelContract after inspecting the clean Git state and history,
automation memory, root/product handoffs, active `To-Sam/` messages, the full
implementation and test surface, both contracts, packaging, and portfolio
validation. No Sam request was active. The required warning-strict Python 3.11
baseline passed all 8 WheelContract, 48 AgentScope, and 53 ProofRun tests with
one expected optional skip.

The release audit exercised metadata, wheel contents, source and installed
invocation, help/version, default and explicit manifests, behavior versus setup
exits, bounded output, failure diagnostics, and Unix child-spawning timeout
cleanup. It found two concrete blockers. First, `--wheel` accepted a project
directory and silently built it even though the option promises a prebuilt
wheel. Second, the Python 3.10 fallback accepted duplicate TOML keys and
sections that Python 3.11+'s standard parser rejects. WheelContract now requires
one existing `.whl` override and rejects fallback duplicates consistently.
Focused regression coverage grew from 8 to 10 tests; schema v1, assertion
behavior, synchronous lifecycle ownership, and exit 0/1/2 remain unchanged.

The audit wheel contains only the intended four package modules, license, entry
point, and standard metadata. Name, version, Python requirement, license,
summary, help, and version are correct. The stale WheelContract v0.1.0 claim in
`products/README.md` was also corrected. With no blocker remaining,
WheelContract was promoted from v0.3.0 to v1.0.0 and frozen as the portfolio's
third local MVP.

Current repository evidence was used to compare four next-product options. A
bounded `ReleaseFact` consistency experiment was selected because today's stale
portfolio version claim demonstrated the problem directly. The next run should
prototype one canonical TOML version plus explicit read-only file claims in a
disposable fixture and retain it only if the config and all-mismatch report are
clearer than focused `rg`/shell. Documentation examples, cross-platform cleanup
coordination, and output-disk limiting were rejected as overlapping, externally
blocked, or speculative.

Final warning-strict Python 3.11 portfolio validation passed all 10
WheelContract, 48 AgentScope, and 53 ProofRun tests with one expected skip. All
three wheels built and isolated-installed, the three-case WheelContract
self-contract and six-case AgentScope contract passed, compilation was clean,
and no human input is needed. A post-commit ProofRun pass also completed with a
valid sealed receipt and applicable named `unit` evidence.

## 2026-09-16 — ReleaseFact v0.1.0 bounded prototype

Started the selected fourth product after inspecting the clean repository,
automation memory, root and product handoffs, active `To-Sam/` communications,
the complete WheelContract implementation and tests, and the portfolio
validator. No Sam request was active. The required warning-strict Python 3.11
baseline passed all 10 WheelContract, 48 AgentScope, and 53 ProofRun tests with
one expected optional skip; all three existing wheels, isolated installs, and
installed behavior contracts passed.

Built dependency-free ReleaseFact around one canonical dotted TOML string and
explicit named file claims. Each claim is an exact complete-line template with
one `{version}` slot and must select exactly one line. The checker reports every
actual value, expected value, file, and line deterministically; exit 0 means all
claims match, 1 means drift, and 2 means the contract or selector is invalid.
Paths stay within the contract directory, unknown fields are rejected, Python
3.11+ uses `tomllib`, and Python 3.10 has a narrow basic-string fallback.

The first fixture models the stale WheelContract portfolio claim with package
v0.2.0, installed contract v0.3.0, and documentation v0.1.0 against canonical
v1.0.0. One run reports all three drifts. Five focused methods cover passing
order, complete diagnostics, ambiguous selectors, strict/path validation, and
the fallback. A local three-claim self-contract and root seven-claim real-
repository contract dogfood package, product docs, and portfolio docs.

The prototype is retained. Although its declaration is slightly longer than
three searches, equivalent reliable shell must independently extract values,
continue after mismatches, validate selector cardinality, preserve order,
separate setup failure, and aggregate output. Centralizing that behavior is a
material clarity and reuse gain. The portfolio validator now tests, builds, and
isolated-installs all four products and runs ReleaseFact from its installed
wheel; the three frozen products were not changed.

Final warning-strict Python 3.11 portfolio validation passed all 5 ReleaseFact,
10 WheelContract, 48 AgentScope, and 53 ProofRun tests with one expected skip.
All four wheels built and isolated-installed, the installed seven-claim
ReleaseFact dogfood and both WheelContract behavior contracts passed, and
focused Python 3.14 tests, source contracts, help, compilation, shell syntax,
and diff checks were clean. No human input is needed. The next run should
rehearse a v0.2 bump in a disposable checkout and change behavior only if the
diagnostics reveal a concrete gap.

## 2026-09-17 — ReleaseFact v1.0.0 release freeze and clean builds

Continued ReleaseFact after inspecting the clean repository, automation memory,
root and product handoffs, active `To-Sam/` communications, product
implementation/tests/docs, contracts, and portfolio validator. No Sam request
was active. The warning-strict Python 3.11 baseline passed all 5 ReleaseFact, 10
WheelContract, 48 AgentScope, and 53 ProofRun tests with one expected optional
skip; all four wheels, installs, and installed contracts passed.

The prescribed disposable release rehearsal changed only ReleaseFact's
canonical version from 0.1.0 to 0.2.0. The root contract reported all seven
stale claims with exact files, lines, actual values, and the expected value.
Following the report updated six claims on the first attempt; ReleaseFact then
caught the one missed root README claim and passed after that final correction.
No diagnostic was ambiguous, redundant, or missing, so schema v1 and checker
behavior remain unchanged.

The release-readiness audit inspected the built wheel members and metadata,
license, entry point, source and isolated-installed commands, help/version,
passing root contract, aggregate drift exit 1, invalid-setup exit 2, docs, five
tests, and Python 3.10 fallback coverage. No product blocker remained.
ReleaseFact was promoted from v0.1.0 to v1.0.0 and frozen as the fourth local
MVP with its read-only schema-v1 contract and exits 0/1/2 intact.

The audit did expose a portfolio-validator defect: its direct wheel builds
refreshed ignored `build/` and `*.egg-info/` paths even though the script claimed
all output was temporary and ordinary Git status stayed clean. Validation now
copies each product into its managed temporary tree before building. A complete
hash inventory of every product file was identical before and after the updated
validator ran, proving the checkout received no new or modified residue.

Final warning-strict Python 3.11 portfolio validation passed all 116 tests with
one expected optional skip, built and isolated-installed all four wheels, and
passed the installed ReleaseFact root contract plus both WheelContract behavior
contracts. Both ReleaseFact source contracts, compilation, shell syntax, and
diff checks passed. The next run should perform the bounded ignored-residue
detector experiment in `NEXT_RUN.md` and retain it only if it improves materially
on focused `find` plus hashing shell. No human input is needed.

## 2026-09-18 — ResidueCheck v0.1.0 bounded prototype

Started the selected fifth-product experiment after inspecting the clean Git
state and history, automation memory, root/product handoffs, active `To-Sam/`
communications, implementation/test surfaces, opportunity record, and portfolio
validator. No Sam request was active. The warning-strict Python 3.11 baseline
passed all 116 existing tests with one expected optional skip, built and
isolated-installed all four frozen products, and passed their contracts.

Built ResidueCheck v0.1.0, a dependency-free single-command residue observer.
It fingerprints one bounded tree before and after a command, including files
that Git ignores, and deterministically reports created, modified, and removed
regular files and symlinks. Literal contained path-prefix exclusions, entry,
per-file, and total-byte bounds, directory-symlink non-traversal, streaming
SHA-256, and an exact display overflow keep traversal and reports explicit.
Clean successful commands exit 0, command failure or residue exits 1, and setup
or inspection failure exits 2.

Seven focused tests cover all three residue kinds, ignored files, clean excluded
trees, pre-command limit enforcement, entry/byte bounds, bounded rendering,
failed commands, unsafe exclusions, and symlink handling. Portfolio validation
now builds and isolated-installs a fifth wheel, then exercises the installed
CLI against three ignored changes before continuing the four frozen products.

The prototype is retained. A portable focused shell equivalent needs two sorted
manifests plus pruning, size accounting, per-file hashing, three-way comparison,
truncation, cleanup, and wrapped-command failure handling. ResidueCheck makes
those mechanics one bounded invocation while exposing the unavoidable cost:
two traversals and two hashes of every included regular byte. No frozen product
behavior changed. The next run should dogfood the installed artifact around a
real wheel build in a disposable source copy, measure its scope and overhead,
and promote/freeze only if fresh and repeated-build diagnostics remain clear.

Final warning-strict Python 3.11 portfolio validation passed all 123 tests with
one expected optional skip, built and isolated-installed all five wheels, and
passed the installed ResidueCheck fixture, ReleaseFact dogfood, WheelContract
self-contract, and AgentScope behavior contract. Focused compilation,
ReleaseFact consistency, shell syntax, and diff checks also passed.

## 2026-09-19 — ResidueCheck v1.0.0 release freeze

Continued ResidueCheck after inspecting the clean Git state/history, automation
memory, all root and product handoffs, active `To-Sam/` communications, product
implementation/tests/docs, opportunity record, and portfolio validator. No Sam
request was active. The warning-strict Python 3.11 baseline passed all 123 tests
with one expected optional skip, all five wheel builds/installs, and every
installed contract.

The prescribed installed-artifact dogfood wrapped a real ReleaseFact PEP 517
wheel build from a clean Git archive. The fresh run named all ten created files
under `build/`, `dist/`, and `src/releasefact.egg-info/`. After one source edit,
the repeated build named only the copied module and rebuilt wheel as modified.
No exclusions were needed. The fresh direct build took about 0.59 seconds and
the wrapped build about 0.68 seconds; a no-op two-snapshot scan took about 0.10
seconds over 38 entries and 49,167 bytes on this host.

The exercise exposed one concrete diagnostic gap: changed reports omitted the
entry/byte scope needed to judge their scan cost. ResidueCheck now reports both
before and after entry and hashed-byte totals on every completed check. It also
renders singular change and entry summaries correctly; focused coverage grew
from seven to eight tests. No configuration, glob, rollback, watcher, sandbox,
or general task-runner behavior was added.

The release audit verified exact wheel members and metadata, installed help and
version, clean/change/setup exits 0/1/2, Python 3.10 grammar compatibility, and
focused warning-strict Python 3.11 plus Python 3.14 behavior. ResidueCheck was
promoted from v0.1.0 to v1.0.0 and frozen as the fifth local MVP.

Repository-local evidence then compared four next opportunities. The selected
bounded experiment is an exact wheel-structure contract for scalar metadata,
console entry points, and package members, retained only if it is materially
clearer than a focused standard-library assertion script. Interpreter discovery,
artifact cleanup, and persistent benchmark reports were rejected as implicit,
destructive, or host-specific.

Final warning-strict Python 3.11 portfolio validation passed all 124 tests with
one expected optional skip, built and isolated-installed all five wheels, and
passed the installed ResidueCheck fixture, ReleaseFact dogfood, WheelContract
self-contract, and AgentScope behavior contract. Focused Python 3.14 tests,
Python 3.10 grammar parsing, wheel audit, compilation, ReleaseFact consistency,
shell syntax, documentation checks, and diff checks passed. No human input is
needed. The next run should execute the bounded experiment in `NEXT_RUN.md`.

## 2026-09-20 — WheelFact v0.1.0 bounded prototype

Started the selected sixth-product experiment after inspecting the clean Git
state and history, automation memory, root and product handoffs, active
`To-Sam/` communications, opportunity record, ResidueCheck implementation and
tests, and the portfolio validator. No Sam request was active. The default
`python3` correctly failed the documented build-backend preflight; explicit
warning-strict Python 3.11 baseline validation passed all 124 existing tests
with one expected optional skip, five wheel builds/installs, and every installed
contract.

Built the frozen ResidueCheck wheel from a disposable source copy and derived a
16-line exact contract for distribution name, version, Python requirement,
license, console entry point, and four package modules. WheelFact v0.1.0 reads
that existing archive without building or installing it, validates one strict
schema-v1 TOML declaration, and reports all unequal, missing, and unexpected
facts deterministically. Matches exit 0, contract mismatches exit 1, and invalid
contracts or artifacts exit 2.

Inspection is explicitly bounded to 10,000 archive entries and 1 MiB for each
decompressed metadata control file; package payloads are named but never
decompressed. Unsafe and duplicate archive paths, ambiguous `.dist-info`
directories, repeated mandatory metadata, malformed entry points, unknown
contract fields, duplicate members, and unsafe contract paths fail explicitly.
The Python 3.10 fallback supports the prototype's multiline member declaration.

Five focused tests cover the exact passing artifact, eight simultaneous scalar,
entry-point, and member mismatches, invalid and ambiguous wheels, strict
contract validation, and fallback parsing. The prototype is retained: a one-off
assertion script is shorter for one wheel, but every release audit would repeat
bounded archive validation, metadata and entry-point parsing, set comparison,
complete diagnostics, and exit semantics. The declaration keeps expectations
clear without overlapping WheelContract's installed behavior.

Portfolio validation now builds and isolated-installs all six products and uses
installed WheelFact to check the real ResidueCheck wheel's nine facts. Final
warning-strict Python 3.11 validation passed all 129 tests with one expected
optional skip, six wheel builds/installs, and every installed contract. Focused
Python 3.14 tests, Python 3.10 grammar parsing, compilation, ReleaseFact
consistency, shell syntax, and diff checks passed. No human input is needed. The
next run should perform the second-artifact diagnostic rehearsal in
`NEXT_RUN.md` and promote only if schema v1 remains sufficient.

## 2026-09-21 — WheelFact v1.0.0 release freeze

Continued WheelFact after inspecting the clean Git state and history,
automation memory, root and product handoffs, active `To-Sam/` communications,
implementation, tests, contracts, and portfolio validator. No Sam request was
active. The warning-strict Python 3.11 baseline passed all 129 tests with one
expected optional skip, built and isolated-installed all six products, and
passed every installed contract.

Built the independent frozen AgentScope wheel from a disposable source copy and
added its exact schema-v1 contract: four scalar metadata facts, one console
script, and four payload members. A deliberately stale 16-line copy changed all
four scalar values, replaced the script, omitted `agentscope/core.py`, and named
an absent member. One WheelFact run reported all eight mismatches while still
showing the three correct member facts; every correction was explicit and no
schema change was needed.

The focused standard-library comparison required 44 lines and still omitted
WheelFact's unsafe and duplicate archive rejection, `.dist-info` ambiguity
checks, control-file limits, strict contract parsing, and stable setup errors.
The exact declaration remains the clearer repeated release-audit interface.
Promoted WheelFact unchanged from v0.1.0 to v1.0.0 and froze schema v1 plus
exits 0/1/2 as the sixth local MVP. Portfolio validation now checks both real
ResidueCheck and AgentScope artifacts with the installed WheelFact command.

Final warning-strict Python 3.11 portfolio validation passed all 129 tests with
one expected optional skip, built and installed all six wheels, and passed both
real WheelFact contracts plus every other installed contract. Focused Python
3.14 tests, Python 3.10 grammar parsing, exact 1.0.0 wheel members and metadata,
TOML parsing, ReleaseFact consistency, shell syntax, and diff checks passed.
All six completed products remain behaviorally frozen. No human input is
needed; the next run should compare at least three fresh, current opportunities
and build one bounded seventh-product prototype rather than extend WheelFact
into general packaging policy.

## 2026-09-22 — GrammarCheck v0.1.0 bounded prototype

Started the seventh-product selection after inspecting the clean Git state and
history, automation memory, root and product handoffs, active `To-Sam/`
communications, the WheelFact implementation and tests, the opportunity record,
workflow, packaging metadata, and portfolio validator. No Sam request was
active. The warning-strict Python 3.11 baseline passed all 129 existing tests
with one expected optional skip, six wheel builds and isolated installs, and
every installed contract.

Compared three fresh repository-grounded opportunities against current
authoritative sources. Target-grammar preflight addressed a repeated manual
Python 3.10 audit and CPython provides the narrow best-effort
`ast.parse(feature_version=...)` primitive. Declared-support/CI-matrix
consistency would require full version-specifier and YAML semantics while the
real hosted matrix already supplies runtime evidence. Reproducible wheel
comparison lacked a demonstrated failure and the ecosystem already standardizes
`SOURCE_DATE_EPOCH`. Ruff owns broader target-version-aware lint and formatting,
so the selected experiment remains dependency-free and grammar-only.

Built GrammarCheck v0.1.0. It selects explicit relative `.py` files and
directories under one root, deduplicates overlaps, rejects symlinks and escapes,
and caps file count, per-file bytes, and aggregate bytes. Each source is parsed
against an explicit older grammar and the AST is then compiled so compiler-only
scope errors are not mistaken for success. Deterministic output reports every
incompatible file and inspection scope; exits 0, 1, and 2 separate compatibility,
incompatibility, and invalid setup.

Four focused methods cover sorted and overlapping passes, Python 3.10-only
syntax under a 3.9 target, compiler-only scope failure, unsafe/missing/empty and
symlink sources, file/byte bounds, target validation, and CLI errors. Installed
portfolio validation now checks source and tests for all seven products against
Python 3.10 grammar. The local host has no Python 3.10 executable, underscoring
the local preflight use case while hosted CI remains authoritative.

Final warning-strict Python 3.11 portfolio validation passed all 133 tests with
one expected optional skip, built and isolated-installed seven wheels, passed
every previous installed contract, and checked 40 Python files totaling 367,624
bytes against target grammar 3.10. Focused tests, self-check, compilation, diff
checks, and the direct aggregate check passed. No frozen behavior changed and
no human input is needed. The next run should inject representative Python
3.11–3.13 syntax in a disposable copy, compare diagnostics with direct AST and
current Ruff output, and freeze or abandon based on clarity.

## 2026-09-23 — GrammarCheck experiment archived

Continued the required GrammarCheck decision rehearsal after inspecting clean
Git state/history, automation memory, root and product handoffs, active
`To-Sam/` communications, implementation/tests, opportunity records, and the
portfolio validator. No Sam request was active. The pre-change warning-strict
Python 3.11 baseline passed all 133 tests with one expected optional skip,
seven wheel builds and isolated installs, and every installed contract.

A disposable five-file fixture included one compatible file, Python 3.11
exception-group syntax, a Python 3.12 type statement, a Python 3.13 type alias
with a default type parameter, and a compiler-only top-level `return`. Against
target 3.10, GrammarCheck returned exit 1 and reported one compatible plus all
four incompatible files with locations, reasons, file count, and byte count.

The comparison did not clear the retention gate. A focused 13-line direct
`ast.parse(feature_version=(3, 10))` and `compile` loop returned exit 1 with the
same four file diagnostics. Ruff 0.16.8 returned exit 1 with richer source
excerpts and five diagnostics, separately identifying the 3.12 type-statement
and 3.13 default-type-parameter incompatibilities in the same file. Ruff's
official settings document `target-version` for minimum-version behavior.

GrammarCheck remains in `products/grammarcheck/` as runnable experiment
evidence, but it is not promoted or actively maintained. Its wheel build,
isolated install, and portfolio scan were removed from the active validator,
returning the maintained portfolio to the six frozen local MVPs. No frozen
product behavior changed. The next run should compare at least three fresh,
repository-grounded opportunities and establish an explicit abandonment gate
before building one bounded prototype. No human input is needed.

Final warning-strict Python 3.11 active portfolio validation passed all 129
maintained tests with one expected optional skip, built and isolated-installed
six wheels, and passed every installed contract. The archived GrammarCheck's
four focused tests also pass independently. ReleaseFact consistency, shell
syntax, compilation, and diff checks passed.

## 2026-09-24 — byte-reproducible wheel validation

Continued the product lab after inspecting the clean Git state and history,
automation memory, root handoffs, active `To-Sam/` communications, product
documentation, packaging metadata, implementation/tests, workflow, and the
portfolio validator. No Sam request was active. The default `python3` correctly
failed the documented `setuptools>=68` preflight; the clean warning-strict
Python 3.11 baseline passed all 129 maintained tests with one expected optional
skip, six wheel builds and isolated installs, and every maintained contract.

Compared three credential-free release-evidence opportunities against current
authoritative sources. A disposable local-link scan found all 24 Markdown
targets present, while mature lychee already owns broader link validation. The
portfolio does not exercise sdists even though PyPA recommends shipping both
sdists and wheels, but the standard `build` frontend is not locally installed
and no sdist-specific defect has yet been demonstrated. Reproducible wheels had
previously been speculative, so it was tested directly before implementation.

Two clean ReleaseFact wheel builds three seconds apart had identical members,
payload CRCs, and sizes but different SHA-256 hashes because generated ZIP entry
timestamps used wall-clock time. Repeating the same experiment with the
standard `SOURCE_DATE_EPOCH` set to the latest Git commit timestamp produced
byte-identical artifacts. This cleared the bounded retention gate without
justifying a seventh CLI: the standard environment variable plus `cmp` is the
transparent complete check for this pure-Python portfolio.

Updated the portfolio validator to require a valid Git commit timestamp, export
it as `SOURCE_DATE_EPOCH`, build every frozen product from two independent
temporary source copies, require exactly one wheel from each build, and reject
any byte drift before the first artifact is installed and exercised. Updated
README, STATUS, NEXT_RUN, and the opportunity record. No frozen product API,
schema, package version, or behavior changed. The final warning-strict Python
3.11 acceptance run passed 129 tests with one expected optional skip, twelve
builds, six reproducibility comparisons, six isolated installs, and all
existing contracts. The next run should rehearse the standard
sdist-to-wheel path in a disposable copy and retain a gate only if it exposes
evidence absent from direct wheels, WheelFact, and WheelContract.

## 2026-09-25 — current license metadata and sdist decision

Continued the six-product portfolio after inspecting the clean Git state and
history, automation memory, root and product handoffs, active `To-Sam/`
communications, opportunity records, packaging definitions, implementation,
tests, workflow, and portfolio validator. No Sam request was active. The clean
warning-strict Python 3.11 baseline passed all 129 maintained tests with one
expected optional skip, twelve reproducible wheel builds, six isolated
installs, and every maintained contract.

Completed the prescribed release-path experiment in a disposable environment
with the standard `build` frontend and Twine. ReleaseFact's sdist-derived wheel
was byte-identical to its direct wheel, installed successfully, and both the
wheel and sdist passed `twine check --strict`. That path added no evidence beyond
the maintained direct-wheel, WheelFact, and WheelContract gates, so no permanent
sdist build dependency or duplicate CI path was retained.

The experiment also built sdists from two separate source copies. They differed
even under the Git-derived `SOURCE_DATE_EPOCH`; decompressed tar hashes differed,
and member inspection showed source-copy and generated-file mtimes. Because the
portfolio does not publish sdists, a custom normalization layer would be
speculative and was rejected.

The standard frontend did expose a concrete release defect: current setuptools
reported every package's `project.license = {text = "MIT"}` form as an overdue
deprecation, and warning-strict wheel metadata generation reproduced it as a
hard failure. Migrated all six maintained products plus archived GrammarCheck
to SPDX `license = "MIT"` and explicit `license-files = ["LICENSE"]`, raised
their declared/validated build backend floor to setuptools 77, and passed build
warning policy into both reproducible-wheel invocations.

The migration changed core metadata from legacy `License` to
`License-Expression`, exposing a real WheelFact compatibility defect. WheelFact
v1.0.1 now prefers the modern header and falls back to the legacy header, with
focused coverage for both and no schema change. Updated portfolio/product docs,
status, handoff, and opportunity evidence. The next run should mutate wheel
`RECORD` digest, size, and membership evidence and extend WheelFact only if the
existing install, structure, and behavior layers demonstrably miss meaningful
corruption.

Final warning-strict Python 3.11 acceptance passed all 130 maintained tests with
one expected optional skip, twelve byte-reproducible wheel builds, six isolated
installs, and every maintained contract. Archived GrammarCheck's four tests,
all seven TOML package metadata declarations, compilation, local Markdown
targets, ReleaseFact consistency, shell syntax, and diff checks also passed.

## 2026-09-26 — WheelFact v1.0.2 RECORD integrity

Continued the six-product portfolio after inspecting the clean Git state and
history, automation memory, root and product handoffs, active `To-Sam/`
communications, WheelFact implementation/tests, opportunity evidence, and the
portfolio validator. No Sam request was active. The clean warning-strict Python
3.11 baseline passed all 130 maintained tests with one expected optional skip,
twelve reproducible wheel builds, six isolated installs, and every maintained
contract.

Executed the prescribed `RECORD` experiment against a real AgentScope wheel.
Separate variants supplied a wrong payload digest, wrong declared size, missing
payload row, and unrecorded archive member. Pip 25.0.1, WheelContract 1.0.0, and
Twine 7.0.0 accepted all four. `wheel unpack` 0.45.1 rejected the bad digest and
both membership failures but accepted the false size. WheelFact v1.0.1 rejected
only the added payload through its exact package-member contract. A focused
33-line standard-library verifier caught every variant but omitted safe paths,
duplicates, hash policy, resource bounds, combined diagnostics, and stable
artifact-error semantics.

This demonstrated correctness gap justified reopening WheelFact narrowly.
Version 1.0.2 verifies strict three-field CSV rows, safe unique paths, complete
archive membership with deprecated signature exceptions, secure supported
hashes, digests, and any declared sizes before evaluating unchanged schema-v1
facts. Payloads are hashed in 64 KiB chunks under a 1 GiB aggregate declared
uncompressed limit. Invalid evidence remains artifact/setup exit 2; contract
mismatches remain exit 1, and no provenance or authenticity claim is implied.

Focused coverage now includes eight test methods and exercises the four real
corruptions plus missing `RECORD`, missing and weak hashes, invalid sizes,
duplicate rows, absent-file rows, and an invalid self row. Warning-strict Python
3.11 and 3.14 focused suites, Python 3.10 grammar parsing, compilation, archived
GrammarCheck tests, ReleaseFact consistency, shell syntax, and diff checks pass.
Final warning-strict portfolio validation passed all 132 maintained tests with
one expected skip, twelve byte-reproducible wheel builds, six isolated installs,
and every installed contract. No human input is required. The next run should
decide whether all six built wheels need a contract-independent integrity gate
without widening WheelFact into a general packaging linter.

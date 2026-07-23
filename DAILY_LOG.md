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

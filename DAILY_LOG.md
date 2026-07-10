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

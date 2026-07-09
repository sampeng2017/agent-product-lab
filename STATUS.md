# ProofRun status

## Current product idea

ProofRun is a local-first CLI that records verification receipts for existing
development commands and binds them to the exact Git working state they covered.

## Current product shape

The repository contains a dependency-free Python CLI with four commands:
`run`, `verify`, `status`, and `history`. Receipts use append-only JSON Lines
under `.proofrun/`, which stays local by default. `verify` reads a
`proofrun.toml` manifest and records a receipt for each named check.

## Completed today

- Added a declarative `proofrun.toml` manifest for named checks.
- Implemented `proofrun verify` with optional check selection and fail-fast
  execution.
- Kept suite execution on the same receipt model as `proofrun run`.
- Added tests for manifest loading, check selection, and fail-fast suite runs.
- Dogfooded the new workflow with this repository's own unit-test command.

## Changed since the previous run

ProofRun moved from individual ad hoc checks to a repeatable suite workflow.
The repository now includes a working manifest and `verify` is the recommended
entry point for routine validation.

## Known issues and incomplete work

- Fingerprinting reads all untracked file contents and may be slow in large
  repositories.
- Status only reports that the working tree changed; it does not yet identify
  which files caused invalidation.
- Receipts are not cryptographically chained or shareable as a report.
- The manifest only supports per-check commands today; there is no first-class
  per-check environment or working-directory override.

## Recommended next step

Explain exactly which tracked or untracked files invalidated a receipt so
`proofrun status` becomes more actionable after agent-driven edits.

## Important decisions

- Local-first and zero runtime dependencies for the initial wedge.
- Evidence is invalidated by commit or working-tree changes and by age.
- Receipts are ignored by Git; product decisions and run handoffs are committed.
- The suite workflow is declarative via `proofrun.toml`, but each check still
  produces its own append-only receipt.

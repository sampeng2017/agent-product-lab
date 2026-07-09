# ProofRun status

## Current product idea

ProofRun is a local-first CLI that records verification receipts for existing
development commands and binds them to the exact Git working state they covered.

## Current product shape

The repository contains a dependency-free Python MVP with three commands:
`run`, `status`, and `history`. Receipts use append-only JSON Lines under
`.proofrun/`, which stays local by default.

## Completed today

- Researched and evaluated three product opportunities.
- Selected ProofRun and documented its user, promise, scope, and roadmap.
- Implemented command execution and receipt recording.
- Implemented Git commit and working-tree fingerprints.
- Implemented validity assessment, JSON output, and history display.
- Added unit tests and setup/run documentation.

## Changed since the previous run

This is the first run; the repository started empty.

## Known issues and incomplete work

- Checks are invoked individually; there is no declarative suite manifest yet.
- Fingerprinting reads all untracked file contents and may be slow in large
  repositories.
- Receipts are not cryptographically chained or shareable as a report.
- A missing executable is recorded as exit 127 but does not include an error
  message in the receipt.

## Recommended next step

Add a small `proofrun.toml` manifest and a `verify` command that runs named
checks as a suite, then dogfood it as this repository's standard validation
entry point.

## Important decisions

- Local-first and zero runtime dependencies for the initial wedge.
- Evidence is invalidated by commit or working-tree changes and by age.
- Receipts are ignored by Git; product decisions and run handoffs are committed.

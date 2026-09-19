# Product lab status

## Current direction

ResidueCheck v0.1.0 is the active fifth-product prototype. ProofRun v1.8.1,
AgentScope v1.0.0, WheelContract v1.0.0, and ReleaseFact v1.0.0 remain frozen.
ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

The prototype addresses a demonstrated portfolio-validator blind spot: commands
can create or refresh Git-ignored files while ordinary Git status remains clean.
Its first bounded fixture and installed artifact prove created, modified, and
removed reporting without relying on Git visibility.

## Product shape

- `products/residuecheck/` contains a dependency-free Python 3.10+ CLI and seven
  focused tests.
- One invocation snapshots a root, runs one command, snapshots again, and emits
  deterministic path-level changes plus the command result.
- Literal path-prefix exclusions, entry/per-file/total-byte limits, symlink
  non-traversal, and change-display limits keep scope explicit.
- Portfolio validation builds and isolated-installs all five products and runs
  the installed ResidueCheck against an ignored-file fixture.

## Completed today (2026-09-18)

- Passed the clean warning-strict 116-test four-product baseline, all wheel
  builds and isolated installs, and existing behavior contracts.
- Reproduced ignored created, modified, and removed residue in a disposable
  fixture and compared the desired report with portable `find`/hash shell.
- Built ResidueCheck v0.1.0 with streamed fingerprints, deterministic comparison,
  three scan bounds, literal exclusions, bounded output, and exits 0/1/2.
- Added seven tests covering the three change kinds, clean exclusions, scan
  preflight, limits, output compaction, command failures, unsafe exclusions,
  and directory-symlink handling.
- Integrated the fifth wheel and an installed ignored-residue check into the
  portfolio validator.

## Changes since the prior run

The repository now contains an active fifth product rather than only a proposed
experiment. No frozen product behavior changed. Portfolio validation gained one
new built/installed artifact and a real three-change installed-CLI assertion.

## Known issues

- ResidueCheck compares boundary state; transient restored changes are invisible.
- It observes and reports but does not isolate or roll back command changes.
- Special filesystem entries and scan races fail explicitly.
- Command output is inherited and unbounded; only the tool's own path report is
  capped. A post-command scan-bound failure cannot enumerate excess residue.
- Exact whole-tree hashing runs twice and is intentionally bounded rather than
  optimized with metadata shortcuts.
- The four frozen products retain their documented limits. Hosted portfolio CI
  remains Ubuntu-only, and the repository has no Git remote.

## Decisions

- Retain ResidueCheck v0.1.0 because one invocation replaces two manifests,
  pruning, size accounting, hashing, comparison, truncation, and failure logic
  that portable shell would need to assemble repeatedly.
- Keep exclusions as literal contained prefixes instead of implicit ignores or
  glob semantics; the point is explicit inspection of Git-ignored files.
- Keep the product a one-command observer, not a task runner, watcher, sandbox,
  rollback tool, or ProofRun extension.
- Keep all four completed products frozen unless validation finds a defect.

## Validation

- Pre-change warning-strict Python 3.11 portfolio validation passed all 116
  existing tests with one expected optional skip and all artifact contracts.
- ResidueCheck's seven focused Python 3.11 tests pass warning-strict.
- Final warning-strict Python 3.11 validation passed all 123 tests with one
  expected optional skip, five wheel builds/installs, the installed ResidueCheck
  fixture, ReleaseFact dogfood, and both WheelContract behavior contracts.
- Compilation, ReleaseFact consistency, shell syntax, and diff checks pass.

## Recommended next steps

1. Run installed ResidueCheck around a real wheel build in a disposable source
   copy; record traversal size, elapsed overhead, and both fresh and repeated
   build diagnostics.
2. Audit Python 3.10, wheel contents/metadata, installed help/version, failure
   exits, and documentation if the real-build dogfood stays clear.
3. Promote/freeze the surface only if that audit exposes no concrete blocker.

No human input is required.

# Product lab status

## Current direction

ResidueCheck v1.0.0 is frozen as the fifth local MVP. ProofRun v1.8.1,
AgentScope v1.0.0, WheelContract v1.0.0, and ReleaseFact v1.0.0 remain frozen.
ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

The completed product closes a demonstrated portfolio-validator blind spot:
commands can create or refresh Git-ignored files while ordinary Git status stays
clean. Real wheel-build dogfood confirmed useful diagnostics and bounded cost.
The next selected experiment is an exact wheel-structure contract derived from
the manual artifact audits repeated for every frozen product.

## Product shape

- `products/residuecheck/` contains a dependency-free Python 3.10+ CLI and eight
  focused tests.
- One invocation snapshots a root, runs one command, snapshots again, and emits
  deterministic path-level changes, the command result, and both scan scopes.
- Literal path-prefix exclusions, entry/per-file/total-byte limits, symlink
  non-traversal, and change-display limits keep scope explicit.
- Portfolio validation builds and isolated-installs all five products and runs
  the installed ResidueCheck against an ignored-file fixture.

## Completed today (2026-09-19)

- Passed the clean warning-strict 123-test, five-wheel portfolio baseline with
  one expected optional skip and every installed contract.
- Wrapped a real ReleaseFact wheel build from a clean Git archive. The fresh run
  named ten created build artifacts; a repeat after one source edit named the
  two actually modified outputs.
- Measured 0.59 seconds direct versus 0.68 seconds wrapped for the fresh build;
  a no-op two-snapshot scan took about 0.10 seconds over 38 entries/49,167 bytes.
- Added before/after entry and hashed-byte scope to every completed report and
  corrected singular result labels, with focused regression coverage.
- Audited wheel members/metadata, installed help/version, exits 0/1/2, Python
  3.10 grammar compatibility, and Python 3.11/3.14 behavior.
- Promoted ResidueCheck to v1.0.0 and froze its narrow contract.

## Changes since the prior run

ResidueCheck advanced from v0.1.0 prototype to frozen v1.0.0 after realistic
fresh/repeated build evidence and a release audit. Reports now expose inspection
scope on changed as well as clean runs. No other product behavior changed.

## Known issues

- ResidueCheck compares boundary state; transient restored changes are invisible.
- It observes and reports but does not isolate or roll back command changes.
- Special filesystem entries and scan races fail explicitly.
- Command output is inherited and unbounded; only the tool's own path report is
  capped. A post-command scan-bound failure cannot enumerate excess residue.
- Exact whole-tree hashing runs twice and is intentionally bounded rather than
  optimized with metadata shortcuts.
- The five frozen products retain their documented limits. Hosted portfolio CI
  remains Ubuntu-only, and the repository has no Git remote.

## Decisions

- Freeze ResidueCheck v1.0.0: real builds showed useful fresh and repeat reports,
  no need for glob/configuration expansion, and acceptable bounded overhead.
- Keep exclusions as literal contained prefixes instead of implicit ignores or
  glob semantics; the point is explicit inspection of Git-ignored files.
- Keep the product a one-command observer, not a task runner, watcher, sandbox,
  rollback tool, or ProofRun extension.
- Explore exact wheel structure separately rather than reopening WheelContract
  or ReleaseFact; abandon it if a short `zipfile` assertion is clearer.
- Keep all five completed products frozen unless validation finds a defect.

## Validation

- Pre-change warning-strict Python 3.11 portfolio validation passed all 123 tests
  with one expected optional skip, five wheel builds/installs, and all contracts.
- ResidueCheck's eight focused tests pass warning-strict on Python 3.11 and on
  Python 3.14; all sources parse under Python 3.10 grammar.
- The release wheel has exactly the four intended modules, license, entry point,
  and standard metadata; installed clean/change/setup probes returned 0/1/2.
- Final warning-strict Python 3.11 portfolio validation passed all 124 tests
  with one expected optional skip, all five wheel builds/installs, and every
  installed contract. Compilation, ReleaseFact consistency, shell syntax,
  documentation checks, and diff checks pass.

## Recommended next steps

1. Prototype the bounded exact wheel-structure contract in `NEXT_RUN.md` against
   the ResidueCheck artifact.
2. Compare its declaration and diagnostics with a focused standard-library
   `zipfile`/metadata script and retain it only if the contract is clearer.
3. Do not reopen any frozen product without a demonstrated defect.

No human input is required.

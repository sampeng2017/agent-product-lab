# Product lab status

## Current direction

GrammarCheck v0.1.0 is the active seventh-product prototype. The six prior local
MVPs remain frozen. The next run should stress the target-grammar diagnostics in
a disposable portfolio copy before deciding whether the wedge deserves a 1.0
freeze.
ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

## Product shape

- `products/grammarcheck/` contains a dependency-free Python 3.10+ CLI and four
  focused tests.
- One invocation checks explicit relative files or directories against an
  explicit Python 3.x grammar, then compiles each AST for scope validation.
- Source paths are contained under `--root`; symlinks and escapes are rejected.
- Defaults cap inspection at 10,000 files, 1 MiB per file, and 50 MiB total.
- Compatible, incompatible, and invalid inspections exit 0, 1, and 2.

## Completed today (2026-09-22)

- Passed the clean warning-strict 129-test, six-wheel portfolio baseline with
  one expected optional skip and every installed contract.
- Compared target-grammar checking, support-matrix consistency, and reproducible
  wheel comparison using repository evidence and current authoritative sources.
- Built GrammarCheck v0.1.0 with deterministic aggregate output, bounds, safe
  path selection, and complete syntax/compiler diagnostics.
- Added four tests covering passes, overlapping paths, post-target syntax,
  compiler-only scope failure, unsafe and empty sets, symlinks, bounds, and CLI
  setup errors.
- Integrated the installed artifact into portfolio validation across source and
  tests for every product.

## Changes since the prior run

The portfolio moved from six frozen products and no active experiment to six
frozen products plus one runnable GrammarCheck prototype. No frozen product
behavior changed.

## Known issues

- CPython documents `feature_version` parsing as best effort, not exact target-
  interpreter emulation.
- A pass says nothing about runtime APIs, dependencies, types, platform behavior,
  or standard-library availability.
- The target must be explicit and no newer than the running interpreter.
- Hosted portfolio CI remains Ubuntu-only, and the repository has no Git remote.

## Decisions

- Select target-grammar preflight because minimum-version syntax drift was the
  only candidate grounded in a repeated local manual check.
- Keep GrammarCheck narrower than Ruff and real interpreter matrices: no lint,
  formatting, imports, dependency resolution, metadata inference, or execution.
- Retain v0.1.0 provisionally because one bounded installed command now checks
  the entire portfolio and distinguishes grammar from compiler-scope failures.

## Validation

- Pre-change warning-strict Python 3.11 portfolio validation passed all 129
  existing tests, builds, isolated installs, and installed contracts.
- GrammarCheck's focused warning-strict tests, self-check, compilation, and diff
  checks pass.
- Final warning-strict validation passed all 133 tests with one expected skip,
  built and isolated-installed seven wheels, and checked 40 Python files
  (367,624 bytes) against target grammar 3.10.
- Final portfolio evidence is recorded in `DAILY_LOG.md`.

## Recommended next steps

1. In a disposable copy, add representative Python 3.11, 3.12, and 3.13 syntax
   to separate files and inspect complete Python 3.10 diagnostics.
2. Compare the same fixture with a focused AST script and current Ruff.
3. Freeze only if GrammarCheck remains materially clearer; otherwise document
   abandonment and remove it from active portfolio validation.

No human input is required.

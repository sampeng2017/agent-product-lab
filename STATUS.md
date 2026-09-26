# Product lab status

## Current direction

GrammarCheck v0.1.0 remains an archived experiment and the six completed local
MVPs remain the maintained portfolio. The prescribed source-distribution
rehearsal did not justify a permanent sdist gate: the sdist-derived ReleaseFact
wheel was byte-identical to the direct wheel, installed correctly, and both
artifacts passed strict Twine checks. The rehearsal did expose overdue license
metadata across every package, so today's improvement modernizes that release
surface and repairs WheelFact's corresponding metadata compatibility gap.
ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

## Product shape

- Six frozen products remain in active portfolio validation: ProofRun,
  AgentScope, WheelContract, ReleaseFact, ResidueCheck, and WheelFact.
- `products/grammarcheck/` remains as runnable decision evidence with four
  tests, but is excluded from the active validator and release portfolio.
- WheelFact v1.0.1 preserves schema v1 while accepting the standard
  `License-Expression` core-metadata header with a legacy `License` fallback.
- Portfolio validation derives `SOURCE_DATE_EPOCH` from the latest Git commit,
  performs two isolated wheel builds per product, and rejects byte drift before
  installing and exercising the first artifact.
- All seven package definitions, including archived GrammarCheck, declare SPDX
  license metadata and their included `LICENSE` file through PEP 639 fields.

## Completed today (2026-09-25)

- Passed the clean warning-strict Python 3.11 baseline: 129 maintained tests,
  one expected optional skip, twelve wheel builds, six isolated installs, and
  every maintained contract.
- Used a disposable standard `build`/Twine environment to create ReleaseFact's
  sdist and direct wheel, build a second wheel from the sdist, install it, and
  check both published artifacts. The wheels were byte-identical and all checks
  passed, so no duplicate sdist path was added to maintained validation.
- Demonstrated that two sdists built from separate source copies are not
  byte-reproducible even with `SOURCE_DATE_EPOCH`; source and generated tar
  member mtimes differ. The portfolio does not publish sdists, so this remains
  documented evidence rather than a speculative normalization layer.
- Replaced the deprecated license table in all package metadata with the SPDX
  expression and explicit license-file fields supported by setuptools 77+.
- Added modern and legacy license-header coverage to WheelFact, promoted the
  maintenance release to v1.0.1, and made warning-strict validation apply to
  wheel builds so the original deprecation now fails the gate.

## Changes since the prior run

The portfolio still has six maintained products and one archived experiment.
Compared with the prior run, package metadata uses current PEP 639 license
fields, the required build backend is setuptools 77+, build deprecations are
enforceable under warning-strict validation, and WheelFact understands both
modern and legacy license metadata. The sdist route was rehearsed but not added
as a redundant permanent gate.

## Known issues

- Hosted portfolio CI remains Ubuntu-only, and the repository has no Git remote.
- The archived GrammarCheck code uses CPython's documented best-effort target
  grammar and is not exact interpreter compatibility evidence.
- The maintained release path still builds wheels directly from source trees;
  a disposable rehearsal found no sdist-derived wheel difference. Standard
  setuptools sdists were not byte-reproducible across source copies because
  tar member mtimes retained wall-clock state.
- Local validation requires an interpreter with `setuptools>=77`; the default
  `python3` on this host fails that preflight, while `python3.11` passes.

## Decisions

- Keep the six product schemas frozen; WheelFact's header selection is a
  backwards-compatible correction for the portfolio's standards migration.
- Use the latest Git commit time as the reproducible source timestamp, following
  the standard `SOURCE_DATE_EPOCH` convention.
- Do not build a wheel-reproducibility product: for this pure-Python portfolio,
  two standard builds plus `cmp` are the clearest complete contract.
- Reject a validation run without a usable Git commit timestamp rather than
  silently falling back to wall-clock time.
- Do not retain an sdist build/Twine dependency until it catches evidence the
  direct-wheel, WheelFact, and WheelContract gates miss.

## Validation

- Pre-change `PYTHON_BIN=python3.11 PYTHONWARNINGS=error
  ./scripts/validate-portfolio.sh` passed all 129 maintained tests with one
  expected skip and all installed contracts.
- The ReleaseFact direct and sdist-derived wheels shared SHA-256
  `081b7aa...f87159`; strict Twine checks and isolated installed version passed.
- Two corresponding sdists had distinct hashes and decompressed tar hashes;
  member inspection attributed the difference to source and generated mtimes.
- The legacy license fixture fails warning-strict wheel metadata generation,
  while the migrated ReleaseFact artifact builds cleanly.
- Post-change warning-strict portfolio validation passed 130 maintained tests
  with one expected optional skip, twelve reproducible builds, six isolated
  installs, and every contract. Archived GrammarCheck's four tests, all seven
  package metadata files, compilation, local links, shell syntax, and diff
  checks also passed.

## Recommended next steps

1. Mutate a disposable wheel's `RECORD` hash, size, and membership separately,
   then test whether current WheelFact, WheelContract, and pip installation
   evidence detects each corruption.
2. Compare any missing evidence with `wheel unpack`, `twine check`, and a short
   standard-library verification before extending WheelFact.
3. Reopen WheelFact only for a demonstrated integrity gap with a narrow,
   deterministic contract; otherwise document the negative result and compare
   fresh repository-grounded opportunities.

No human input is required.

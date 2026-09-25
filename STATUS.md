# Product lab status

## Current direction

GrammarCheck v0.1.0 is an archived experiment, not a seventh maintained
product. Its required diagnostic rehearsal failed the retention threshold. The
six completed local MVPs remain frozen.
ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.
Today's release-evidence improvement stays at the portfolio layer: every wheel
must now reproduce byte for byte across two independent source copies. The next
run should examine the separate sdist path without reopening GrammarCheck.

## Product shape

- Six frozen products remain in active portfolio validation: ProofRun,
  AgentScope, WheelContract, ReleaseFact, ResidueCheck, and WheelFact.
- `products/grammarcheck/` remains as runnable decision evidence with four
  tests, but is excluded from the active validator and release portfolio.
- No frozen product behavior or public schema changed in this run.
- Portfolio validation derives `SOURCE_DATE_EPOCH` from the latest Git commit,
  performs two isolated wheel builds per product, and rejects byte drift before
  installing and exercising the first artifact.

## Completed today (2026-09-24)

- Passed the clean warning-strict Python 3.11 baseline: 129 maintained tests,
  one expected optional skip, six wheel builds and isolated installs, and every
  maintained contract.
- Checked 24 local Markdown targets and found no broken documentation links;
  mature link checkers already own broader URL validation.
- Reproduced wheel nondeterminism with two clean ReleaseFact builds: payloads,
  sizes, and CRCs matched, but wall-clock ZIP timestamps changed the SHA-256.
- Rebuilt twice with the Git commit timestamp in `SOURCE_DATE_EPOCH`; both
  artifacts had the same SHA-256.
- Added the successful experiment as a twin-build gate for all six maintained
  products rather than creating a redundant seventh CLI.

## Changes since the prior run

The portfolio still has six frozen products and one archived experiment. Its
validator now proves that repeated builds of every maintained wheel are
byte-identical, instead of merely checking one ephemeral artifact's contents and
installed behavior.

## Known issues

- Hosted portfolio CI remains Ubuntu-only, and the repository has no Git remote.
- The archived GrammarCheck code uses CPython's documented best-effort target
  grammar and is not exact interpreter compatibility evidence.
- The release path still builds wheels directly from source trees; it does not
  build, inspect, or install through source distributions.
- Local validation requires an interpreter with `setuptools>=68`; the default
  `python3` on this host fails that preflight, while `python3.11` passes.

## Decisions

- Keep the six product APIs frozen; the demonstrated defect was in portfolio
  release evidence, not product behavior.
- Use the latest Git commit time as the reproducible source timestamp, following
  the standard `SOURCE_DATE_EPOCH` convention.
- Do not build a wheel-reproducibility product: for this pure-Python portfolio,
  two standard builds plus `cmp` are the clearest complete contract.
- Reject a validation run without a usable Git commit timestamp rather than
  silently falling back to wall-clock time.

## Validation

- Pre-change `PYTHON_BIN=python3.11 PYTHONWARNINGS=error
  ./scripts/validate-portfolio.sh` passed all 129 maintained tests with one
  expected skip and all installed contracts.
- The negative reproduction produced distinct ReleaseFact wheel hashes after a
  three-second delay; the fixed-timestamp reproduction produced identical
  hashes after the same delay.
- Post-change warning-strict portfolio validation passed 129 tests with one
  expected optional skip, twelve wheel builds, six byte comparisons, six
  isolated installs, and every maintained contract.

## Recommended next steps

1. Rehearse the standard sdist-to-wheel install path in a disposable product
   copy and identify whether it exposes a real gap.
2. Compare any proposed gate with `build`, `twine check`, and existing archive
   content tools; do not create another general packaging checker.
3. Retain new validation only if it proves evidence missing from the current
   direct wheel, exact-structure, and installed-behavior checks.

No human input is required.

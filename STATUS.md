# Product lab status

## Current direction

The six completed local MVPs remain the maintained portfolio and GrammarCheck
remains archived. Portfolio validation now applies WheelFact's tested bounded
structure and `RECORD` integrity checks to every built wheel without duplicating
exact package expectations or adding another command-line mode.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- ProofRun, AgentScope, WheelContract, ReleaseFact, ResidueCheck, and WheelFact
  remain frozen and covered by portfolio validation.
- `products/grammarcheck/` remains runnable decision evidence with four tests,
  but is excluded from active validation and the release portfolio.
- WheelFact v1.0.3 keeps schema v1 and the exact-contract CLI unchanged. Its
  `verify_wheel_integrity` library hook reuses the same safe archive inventory,
  complete `RECORD` membership, secure hash, and declared-size validation.
- Portfolio validation derives `SOURCE_DATE_EPOCH` from the latest Git commit,
  performs two isolated wheel builds per product, rejects byte drift, checks
  all six first artifacts for integrity, and then installs and exercises them.

## Completed today (2026-09-27)

- Passed the clean warning-strict Python 3.11 baseline: 132 maintained tests,
  one expected optional skip, twelve reproducible wheel builds, six isolated
  installs, and every maintained contract.
- Compared the three prescribed coverage options. Six additional exact
  contracts would duplicate volatile package expectations; a new integrity-only
  CLI mode would widen WheelFact's stable interface for a portfolio-internal
  use case; a narrow library hook reuses the proven validation with neither
  cost.
- Refactored WheelFact's archive checks into one shared path and exposed
  `verify_wheel_integrity(Path)` without changing the existing CLI, schema, or
  exits.
- Added focused coverage proving the hook accepts internally consistent wheels
  regardless of exact metadata and payload facts while rejecting a corrupt
  digest.
- Added a final portfolio gate that checks all six independently built wheels
  through the installed WheelFact artifact.
- Promoted WheelFact to v1.0.3 and updated portfolio and product documentation.

## Changes since the prior run

Previously only the ResidueCheck and AgentScope exact WheelFact contracts
triggered `RECORD` verification. All six built wheels now receive the same
contract-independent integrity check after their normal build, reproducibility,
install, behavior, and selected exact-contract validation. No other product API,
schema, or package version changed.

## Known issues

- Hosted portfolio CI remains Ubuntu-only, and the repository has no Git remote.
- The archived GrammarCheck code uses CPython's documented best-effort target
  grammar and is not exact interpreter compatibility evidence.
- Standard setuptools sdists were not byte-reproducible across source copies in
  the prior rehearsal because tar member mtimes retained wall-clock state; the
  portfolio does not publish sdists.
- Local validation requires an interpreter with `setuptools>=77`; the default
  `python3` on this host fails that preflight, while `python3.11` passes.
- Internal `RECORD` consistency is not provenance, authenticity, or signature
  verification. WheelFact deliberately makes no such claim.

## Decisions

- Keep exact WheelFact contracts only where stable metadata, entry-point, and
  payload expectations provide distinct value: ResidueCheck and AgentScope.
- Do not add an integrity-only CLI mode. The portfolio-owned adapter is short,
  and the tested library hook preserves WheelFact's exact-contract CLI boundary.
- Run the all-wheel gate after every product has been built so one deterministic
  loop covers exactly the six artifacts already selected by validation.
- Freeze WheelFact v1.0.3 with schema v1 and CLI exits 0/1/2 unchanged.

## Validation

- Pre-change `PYTHON_BIN=python3.11 PYTHONWARNINGS=error
  ./scripts/validate-portfolio.sh` passed 132 maintained tests with one expected
  skip and every installed contract.
- Focused warning-strict WheelFact tests pass nine methods, including the new
  contract-independent acceptance and corruption rejection.
- Final warning-strict Python 3.11 portfolio validation passed 133 maintained
  tests with one expected skip, twelve byte-reproducible wheel builds, six
  isolated installs, every installed contract, and six explicit integrity
  passes.
- Final acceptance commands and post-commit proof are recorded in
  `DAILY_LOG.md`.

## Recommended next steps

1. Compare at least three fresh repository-grounded opportunities before
   changing a frozen product.
2. Favor a bounded experiment with a demonstrated local failure and an explicit
   abandonment gate; avoid release checks already covered by reproducibility,
   WheelFact, WheelContract, or ReleaseFact.
3. Keep the six product schemas and command-line contracts frozen absent a
   demonstrated correctness or safety defect.

No human input is required.

# Product lab status

## Current direction

GrammarCheck v0.1.0 remains archived and the six completed local MVPs remain
the maintained portfolio. Today's bounded wheel-integrity experiment exposed a
real standards and tooling gap: common install, behavior, and publishing checks
accepted inconsistent `RECORD` evidence. WheelFact v1.0.2 now closes that gap
without changing its schema or contract facts.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six frozen products remain in active portfolio validation: ProofRun,
  AgentScope, WheelContract, ReleaseFact, ResidueCheck, and WheelFact.
- `products/grammarcheck/` remains runnable decision evidence with four tests,
  but is excluded from active validation and the release portfolio.
- WheelFact v1.0.2 preserves schema v1, supports modern and legacy license
  metadata, and verifies complete `RECORD` membership, secure hashes, and any
  declared sizes before evaluating exact contract facts.
- Portfolio validation derives `SOURCE_DATE_EPOCH` from the latest Git commit,
  performs two isolated wheel builds per product, rejects byte drift, and then
  installs and exercises the first artifact.

## Completed today (2026-09-26)

- Passed the clean warning-strict Python 3.11 baseline: 130 maintained tests,
  one expected optional skip, twelve reproducible wheel builds, six isolated
  installs, and every maintained contract.
- Built one AgentScope wheel and produced separate bad-digest, bad-size,
  missing-row, and unrecorded-member variants without changing payloads shared
  by the other cases.
- Demonstrated that pip 25.0.1, WheelContract 1.0.0, and Twine 7.0.0 accepted
  all four corruptions. `wheel unpack` 0.45.1 caught the digest and membership
  failures but accepted the wrong size. Pre-fix WheelFact rejected only the
  unrecorded payload because its exact member contract ignored `RECORD`.
- Compared a focused 33-line standard-library verifier, which caught all four
  variants but omitted safe-path validation, duplicate handling, hash-policy
  checks, resource bounds, and stable artifact-error diagnostics.
- Added bounded streaming `RECORD` verification to WheelFact: strict CSV shape,
  safe and unique rows, complete archive membership, secure supported hashes,
  digest equality, provided-size equality, signature exceptions, and a 1 GiB
  aggregate uncompressed limit.
- Added regression coverage for all four demonstrated corruptions, promoted
  WheelFact to v1.0.2, and updated portfolio and product documentation.

## Changes since the prior run

The portfolio still has six maintained products and one archived experiment.
Compared with the prior run, WheelFact no longer treats a structurally matching
but internally inconsistent wheel as valid. The exact TOML schema, contract
facts, and exit 0/1 behavior are unchanged; invalid `RECORD` evidence is an
artifact/setup error with exit 2.

## Known issues

- Hosted portfolio CI remains Ubuntu-only, and the repository has no Git remote.
- The archived GrammarCheck code uses CPython's documented best-effort target
  grammar and is not exact interpreter compatibility evidence.
- Standard setuptools sdists were not byte-reproducible across source copies in
  the prior rehearsal because tar member mtimes retained wall-clock state; the
  portfolio does not publish sdists.
- Local validation requires an interpreter with `setuptools>=77`; the default
  `python3` on this host fails that preflight, while `python3.11` passes.
- Portfolio dogfood applies WheelFact's exact contracts to two representative
  artifacts, not every built wheel. All six are still installed and exercised,
  but pip 25.0.1 did not enforce `RECORD` in this experiment.

## Decisions

- Reopen frozen WheelFact only for the demonstrated correctness defect; retain
  exact schema v1 and the established exit contract.
- Treat malformed or inconsistent `RECORD` data as an invalid artifact (exit 2),
  not a user-owned contract mismatch (exit 1).
- Verify provided sizes even though installed-project `RECORD` allows them to be
  omitted; wheel hashes remain mandatory for every non-signature file except
  `RECORD` itself.
- Stream payload verification and reject more than 1 GiB of declared
  uncompressed content instead of loading package members into memory.
- Do not claim provenance or authenticity: internal `RECORD` consistency is not
  an external signature or trusted-source guarantee.

## Validation

- Pre-change warning-strict portfolio validation passed 130 maintained tests
  with one expected skip and every installed contract.
- The disposable five-artifact matrix recorded exact exits for pip, WheelFact,
  WheelContract, `wheel unpack`, Twine, and the focused verifier.
- Focused WheelFact tests pass eight methods, including the four new real
  corruption regressions; clean AgentScope passes and all variants now exit 2
  with specific diagnostics.
- Final acceptance commands and post-commit proof are recorded in
  `DAILY_LOG.md`.

## Recommended next steps

1. Add a contract-independent, read-only portfolio integrity gate only if it can
   cover all six built wheels without duplicating WheelFact's exact-contract
   interface or weakening its narrow scope.
2. Otherwise compare at least three fresh repository-grounded opportunities and
   select one bounded experiment with an explicit abandonment gate.
3. Keep the six product schemas frozen absent another demonstrated defect.

No human input is required.

# Product lab status

## Current direction

The six maintained tools retain their existing product shapes. WheelContract
v1.0.1 closes a reproduced false passing JSON assertion: booleans and numbers
cannot satisfy each other's expectations. Schema v1 and exit 0/1/2 stay stable.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- ProofRun, AgentScope, WheelContract, ReleaseFact, ResidueCheck, and WheelFact
  remain maintained; GrammarCheck remains archived decision evidence.
- WheelContract v1.0.1 adds a correctness patch, not a new contract format.
- Root CI uses explicit Ubuntu 24.04 across Python 3.10–3.14. Follow
  `docs/CI_PLATFORM.md` and review the platform choice by November 5.
- The installation guide and three runnable examples remain public entry points.

## Completed today (2026-10-06)

- Started clean at `01c44a4`; no active Sam communication was present.
- Verified MIT, zero public issues, and green hosted run `37410408966`.
- Reproduced the JSON scalar bug with a real installed fixture before editing
  the checker: both boolean/number mismatch cases incorrectly passed.
- Corrected comparison while preserving numeric 1/1.0 equality and strings.
- Added matching/mismatching cases, all-field diagnostics, CLI exit 1, and
  aggregate-result assertions. Updated runtime/package versions and self-contract.
- Built and isolated-installed the corrected checker; its regression passed
  without checkout imports. Refresh its public install pin after publication.

## Changes since the prior run

Yesterday documented the existing CI platform. Today corrects adopter-visible
release checking. The other five products, interpreter matrix, and public
schemas are unchanged.

## External-user value

A numeric readiness flag cannot pass a boolean assertion, and a boolean
schema/version field cannot pass a numeric assertion. Both errors previously
escaped otherwise strict installed-artifact contracts.

## Known issues

- The guide's WheelContract install pin must advance to the validated patch.
  Other tools retain their existing tested source pin; build dependencies vary.
- No tagged or package-index release is advertised.
- Hosted validation is Ubuntu-only; Windows example replay is not verified.
- Hosted images update despite an explicit OS label. Ubuntu 26.04 needs a trial.
- Source distributions are not published or proven byte-reproducible.
- Local validation needs setuptools>=77; use a suitable interpreter.
- Wheel integrity and receipt chaining are consistency evidence, not signatures.
- Product profiles and selectors retain the limits in their individual READMEs.

## Decisions

- Reopen a frozen product only for the demonstrated false passing check.
- Separate booleans from numeric values; preserve numeric value equality.
- Keep schema v1 and existing diagnostics/exits, reporting every wrong field.
- Refresh only WheelContract's installation revision after validated publication.

## Validation

- Baseline portfolio: 133 tests, one expected skip, twelve reproducible builds,
  six installs, all release/behavior contracts, and six integrity checks.
- Corrected portfolio: 134 tests with one expected skip and the same artifact
  checks passed. The built v1.0.1 regression also checks CLI exit and totals.
- ReleaseFact and whitespace checks pass; hosted CI must validate the pushed patch.

## Recommended next steps

1. Complete and verify the public WheelContract installation-pin refresh.
2. Investigate further JSON decoding edge cases only through a reproducible
   contract; retain existing numeric compatibility.
3. Follow the platform policy review deadline rather than redoing its decision.

No human input is required.

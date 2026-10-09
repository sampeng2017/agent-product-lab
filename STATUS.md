# Product lab status

## Current direction

WheelContract v1.0.3 turns a reproduced JSON decoder-depth crash into a bounded
case failure and continues later cases. Decoder limits, schema v1, and exits
0/1/2 remain in place. The other maintained tools retain their product shapes.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six tools retain source/build/install/contract validation; GrammarCheck is archived.
- Root CI uses Ubuntu 24.04 and Python 3.10–3.14; review policy by November 5.
- The install guide and three worked examples remain public entry points.
- WheelContract correctness patches preserve its bounded artifact-checking scope.

## Completed today (2026-10-09)

- The October 8 scheduled turn resumed October 9 from clean synchronized 2cdec4c.
  Read memory, Git history, docs, implementation/tests, and active Sam messages.
- Reproduced an uncaught RecursionError on a roughly 10 KB JSON document, below
  the configured byte bound; it aborted the suite before the normal second case.
- Added a real installed-fixture regression first, then handled only the decoder
  recursion failure as a case error with a stable, bounded diagnostic.
- Regression checks child exit 0 versus case failure, continuation, CLI exit 1,
  and aggregate results. Bumped package/runtime/self-contract/docs to 1.0.3.
- Refresh only WheelContract's published installation pin after acceptance.
- Hosted Linux accepted the initial depth fixture. Made the decoder-error
  regression deterministic while keeping normal output parsed by the real
  decoder; no runtime depth limit changed.

## Changes since the prior run

The prior patch rejected nonstandard constants. This patch makes an existing
decoder limit a reported behavior failure rather than an exception escaping
the complete-reporting contract. No limit is raised and no option/schema added.

## External-user value

One deeply nested output can no longer hide results from later release checks.
Users receive a concise reason and the complete suite summary without a traceback.

## Known issues

- The guide selects the v1.0.3 correction; other tools keep their pins.
- Validation applies to cases declaring JSON expectations; decoder limits and
  duplicate-name semantics remain defaults, not a general schema engine.
- No tagged/package-index release is advertised; dependencies resolve separately.
- Hosted checks are Ubuntu-only; Windows replay remains unverified.
- Source distributions are not published or proven byte-reproducible.
- Integrity/chaining are consistency evidence, not authentication.

## Decisions

- Fix the demonstrated suite-abort defect rather than changing recursion limits.
- Report this output failure as exit 1; preserve setup exit 2 and complete results.
- Retain prior JSON compatibility and publish only after acceptance checks.

## Validation

- Baseline had 135 tests and existing build/install/contracts.
- New regression was red with an uncaught RecursionError before the patch.
- Corrected portfolio: 136 tests with one expected skip, twelve reproducible
  builds, six installs, release/behavior contracts, and integrity checks passed.
- The published repair revision installed v1.0.3 and passed the deterministic
  continuation regression. Hosted run 37947298474 passed Python 3.10–3.14.
- Forty local links/anchors passed; older install section anchors remain usable.

## Recommended next steps

1. Preserve complete suite reporting when considering any future decoder issue.
2. Compare concrete user friction with independently reproduced correctness gaps.
3. Follow the November 5 platform-policy review.

No human input is required.

# Product lab status

## Current direction

WheelContract v1.0.5 rejects malformed UTF-8 in JSON assertion output rather than
silently replacing bytes and accepting altered data. Readable previews and
non-JSON checks remain compatible. The CI starter and other maintained products
retain their existing scope.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six maintained products; GrammarCheck stays archived.
- Root CI: Ubuntu 24.04 / Python 3.10–3.14, with the November 5 policy review.
- Individual installation, three local replays, and an external CI starter remain
  the public adoption surfaces. No new mandatory internal gate is added.

## Completed today (2026-10-12, resumed at 20:49 PDT)

- Started clean at synchronized be4bde1. Inspected memory, Git/history, root and
  product docs, implementation/tests, active To-Sam, workflow/validator, and GitHub.
  Public MIT detection and baseline matrix 38107663882 were healthy.
- Baseline warning-strict portfolio passed 138 tests with one expected optional
  skip and all existing builds, installs, contracts, and integrity checks.
- Compared another adoption handoff with a concrete output-validation defect.
  Installed fixtures with an invalid byte, invalid continuation, and encoded
  surrogate all passed JSON assertions after replacement decoding. One invalid
  byte even falsely matched an expected literal U+FFFD.
- Added the regression before the fix and observed all seven cases passing,
  including the three malformed ones that should fail.
- Preserve bounded raw bytes for JSON validation; decode strictly before parsing,
  report a concise case error, and continue the remaining suite. Keep replacement
  decoding solely for readable presentation and non-JSON matching.
- Positive cases cover ASCII, valid Unicode, real U+FFFD, and unchanged human
  output. A separate limit-split case preserves the byte-bound error without
  falsely accusing a valid character of malformed encoding.
- Updated runtime/package/self-contract/docs to 1.0.5. Refresh only WheelContract's
  installation and CI starter revision after published acceptance.

## Changes since the prior run

The prior run supplied a CI adoption starter without runtime changes. This run
repairs an independently reproduced false pass in that checker's existing JSON
surface. No schema, limits, options, dependencies, or generic Unicode policy added.

## External-user value

A package cannot pass its JSON release contract by emitting corrupt bytes that
the checker repairs into apparently valid values. Users retain readable failure
previews, complete suite results, and valid Unicode compatibility.

## Known issues

- UTF-8 validation applies to stdout of cases declaring JSON expectations;
  ordinary stdout/stderr presentation remains replacement-decoded.
- Oversized output already fails its byte bound. A cut through a multibyte
  character does not establish that the original stream was malformed.
- Decoder depth and duplicate-name semantics remain interpreter defaults;
  escaped Unicode values are not subject to a new schema policy.
- CI starter still targets setuptools/no runtime dependencies and was locally
  rehearsed, not hosted as a separate external-project workflow.
- Windows live evidence and package-index/tagged distribution remain absent.
- Source pins do not lock build dependencies; integrity is not authentication.

## Decisions

- Fix the demonstrated validation/presentation conflation instead of adding
  a speculative decoder rule or another example for symmetry.
- Retain human output compatibility and report output failure as exit 1, not
  manifest/setup exit 2. Do not increase output or recursion limits.
- Publish the correction only after full acceptance and update consumer pins
  together, including the external starter.

## Validation

- New installed-fixture regression was red before implementation.
- Both UTF-8-focused tests pass after the fix, including CLI totals and the
  byte-bound split, on local Python 3.11 and 3.14.
- Corrected warning-strict portfolio passed 140 tests with one expected skip,
  twelve reproducible builds, six installs, release/behavior contracts, and
  complete wheel integrity.
- Published 73a5e14 passed CI 38344331849 on Python 3.10–3.14. Its fresh exact
  VCS install passed both new regressions without checkout imports. Install and
  starter pins now select that revision; older install anchors remain usable.
- Consumer revalidation passed the full 140-test portfolio and all artifact
  checks again. Forty-eight local links/anchors and the starter pin check passed;
  the existing installed missing-command replay still diagnoses and corrects
  its fixture without changing the contract.

## Recommended next steps

1. Keep validation of original data separate from display normalization.
2. Assess concrete adopter workflows before another frozen-runtime change.
3. Retain the November 5 platform-policy review.

No human input is required.

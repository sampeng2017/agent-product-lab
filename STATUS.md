# Product lab status

## Current direction

WheelContract v1.0.2 fixes a reproduced false passing JSON-output check:
bare NaN, Infinity, and -Infinity are rejected in cases with JSON expectations,
including nested and unasserted values. Valid strings and numeric compatibility
remain unchanged. The other five maintained tools retain their product shapes.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six maintained tools remain covered by source, build, install, and contract
  validation. GrammarCheck is archived.
- WheelContract uses schema v1 and exits 0/1/2; only correctness patches reopen
  its frozen feature boundary.
- Root CI uses Ubuntu 24.04 and Python 3.10–3.14. Review platform policy by
  November 5. The installation guide and three worked examples remain public.

## Completed today (2026-10-07)

- Inspected clean synchronized 893930c, Git history, docs/source/tests, active
  Sam communications, and the public GitHub surface.
- Confirmed MIT, zero issues, and green hosted run 37565945139.
- Added a real installed-fixture regression first: five nonstandard constant
  cases incorrectly passed, including unasserted nested arrays/objects.
- Configured the JSON decoder to reject those tokens and report case failures;
  preserved existing syntax-error diagnostics and continued suite evaluation.
- Regression covers quoted-string positives, CLI exit 1, and aggregate totals.
- Bumped package/runtime/self-contract/docs to 1.0.2; the public guide now
  selects its verified correction, with older section anchors preserved.

## Changes since the prior run

Version 1.0.1 fixed boolean/number equality. This patch closes invalid JSON
output slipping through when asserted fields happen to match. No schema,
command-line option, dependency, or interpreter matrix changes were needed.

## External-user value

Release checks now detect output that standard JSON consumers reject even when
the checked readiness field looks correct. Diagnostics identify the offending
constant and the suite continues reporting other cases.

## Known issues

- WheelContract's guide selects the v1.0.2 correction; other tools keep their
  current pins. Build dependencies resolve separately.
- JSON validation applies only to cases declaring JSON expectations.
- Decoder limits and duplicate-name behavior otherwise remain Python defaults.
  The patch does not promise a general JSON-schema validator.
- No tagged or package-index release is advertised.
- Hosted validation is Ubuntu-only; Windows replay is not verified.
- Hosted images update despite OS selection; follow the November 5 policy review.
- Source distributions are not published or proven byte-reproducible.
- Integrity/chaining are consistency evidence, not signatures.

## Decisions

- Prefer a demonstrated consumer-visible correctness defect over more examples.
- Use the standard decoder hook rather than textual searches or regexes, so
  quoted strings are never confused with bare tokens.
- Reject invalid output as behavior exit 1; preserve setup exit 2 and schema v1.
- Refresh the public source pin only after the published artifact passes tests.

## Validation

- Baseline: 134 tests with one expected skip plus the existing twelve builds,
  six installs, release/behavior contracts, and wheel integrity checks passed.
- Corrected portfolio: 135 tests with one expected skip, twelve reproducible
  builds, six installs, release/behavior contracts, and six integrity checks pass.
- The newly built/isolated-installed v1.0.2 checker passes the regression without
  checkout imports, including CLI exit and totals. ReleaseFact/diff checks pass.
- Exact GitHub VCS installation and regression passed in a fresh environment.
  Hosted run 37720757395 passed Python 3.10–3.14; 40 local links/anchors pass.

## Recommended next steps

1. Keep the installation pin on the verified correctness patch.
2. Evaluate decoder edge cases only with a concrete failing contract and an
   explicit compatibility decision; avoid claiming universal validation.
3. Review the CI platform by November 5 or an earlier relevant event.

No human input is required.

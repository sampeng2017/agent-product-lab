# Product lab status

## Current direction

WheelContract v1.0.4 reports installed-command launch errors per case and
continues the suite. It preserves schema v1, exits 0/1/2, and its bounded
artifact-checking scope. Other maintained tools retain their product shapes.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six tools retain source/build/install/contract validation; GrammarCheck is archived.
- Root CI uses Ubuntu 24.04 and Python 3.10–3.14; review policy by November 5.
- The install guide and three worked examples remain public entry points.
- WheelContract correctness patches preserve complete reporting.

## Completed today (2026-10-09, evening run)

- Started clean at synchronized 76dab9a. Inspected memory, Git/history, root and
  product documentation, implementation/tests, active To-Sam, and public GitHub.
  Public MIT detection and the latest full Python matrix were healthy.
- Baseline warning-strict portfolio passed 136 tests with one expected skip,
  reproducible builds, isolated installs, release/behavior contracts, and integrity.
- Compared first-use friction with a concrete failure of the documented promise
  to execute every case. A real wheel installed an executable script naming an
  unavailable interpreter; its launch raised FileNotFoundError and aborted the
  suite before the next valid command. The regression was red before the fix.
- Catch only OSError from case process creation. Report a bounded OS reason and
  command name, without temporary paths, fabricated child exit codes, or output.
  Continue later cases and return behavior exit 1, not setup exit 2.
- Added real Unix installed-script/CLI continuation coverage and a portable
  permission-error diagnostic bound test. Promoted package/runtime/self-contract
  to 1.0.4 and updated public behavior documentation and stale product handoff.
- Advance only WheelContract's public install pin after acceptance; other five
  products keep their validated revisions.

## Changes since the prior run

The morning correction contained decoder nesting failures. This independent
patch contains operating-system launch failures for installed commands that
exist but cannot execute. Manifest, build, and installation handling is unchanged.

## External-user value

A broken packaged script no longer hides other release-check results behind a
traceback. Maintainers see which command could not start, an OS reason, results
from later checks, and a complete failure summary.

## Known issues

- Command launch may fail because of a packaged script or a host restriction;
  the diagnostic reports the OS reason, not an inferred packaging root cause.
- The real interpreter-launch fixture is Unix-only; portable error handling is
  tested, but Windows execution and worked examples are not live-tested.
- JSON decoder limits and duplicate-name semantics remain defaults.
- No tagged/package-index release is advertised; build dependencies resolve separately.
- Source distributions are not published or proven byte-reproducible.
- Integrity/chaining are consistency evidence, not authentication.

## Decisions

- Repair reproduced complete-reporting defects, not hypothetical new policy.
- Treat a failed case start as behavior failure; do not broaden the catch to
  filesystem setup or arbitrary exceptions.
- Keep missing-command behavior, timeout cleanup, JSON compatibility, schema,
  and setup exit 2 unchanged.
- Correct stale status references rather than beginning an already finished
  ReleaseFact experiment or implying only three products are validated.

## Validation

- New installed-script regression reproduced the uncaught launch error before
  the patch; focused continuation and diagnostic tests pass afterward.
- Warning-strict portfolio passed 138 tests with one expected optional skip,
  twelve reproducible builds, six isolated installs, release/behavior contracts,
  and complete wheel integrity. WheelContract's 15 tests also pass on Python 3.14.
- Public installation pin must select an acceptance-tested revision.

## Recommended next steps

1. Preserve complete reporting and separate setup errors from case failures.
2. Compare concrete first-user friction before reopening frozen runtime behavior.
3. Follow the November 5 platform-policy review.

No human input is required.

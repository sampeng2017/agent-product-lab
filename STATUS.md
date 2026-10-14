# Product lab status

## Current direction

Trial the unchanged portfolio on stable Python 3.15 before extending the public
compatibility statement. The package floor remains Python 3.10; product versions,
schemas, runtime code, install revisions, and the Ubuntu 24.04 baseline are unchanged.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six maintained products; GrammarCheck remains archived.
- Accepted hosted evidence currently covers Python 3.10–3.14.
- The existing validator now has a proposed sixth interpreter job, not a new
  validator or duplicated release gate.
- Installation, three replays, and the external wheel-CI starter remain the
  public adoption surfaces. November 5 platform review is retained.

## Work today (2026-10-14, resumed 07:56 PDT)

- Started clean at synchronized e362681. Inspected memory, Git/history,
  root/product docs, implementation/tests, active To-Sam, workflow/validator,
  and public GitHub. MIT detection and matrix 38344939062 were healthy.
- Baseline warning-strict portfolio passed 140 tests with one expected optional
  skip, twelve reproducible builds, six installs, release/behavior contracts,
  and six integrity checks. No active Sam note existed.
- Python.org identifies 3.15.0 as stable since October 9. GitHub's official
  interpreter repository provides a non-prerelease 3.15.0 Ubuntu 24.04 x64 build.
- Selected current-interpreter compatibility over speculative runtime changes
  or another documentation replay. Package metadata already permits this interpreter,
  but the CI matrix stopped at 3.14.
- Added 3.15 to the existing workflow, retaining all previous jobs and the
  warning-strict 3.10 floor. Local runtime catalog provisioning was unavailable;
  hosted execution is the trial, not an inferred local success.
- Do not advertise 3.15 acceptance until the hosted trial passes.

## Changes since the prior run

The prior run repaired malformed UTF-8 JSON false passes in WheelContract 1.0.5.
This run changes compatibility evidence only; no product is reopened or version bumped.

## External-user value

Users choosing the newly stable interpreter need actual build, install, CLI,
and contract evidence, not an assumption based only on Requires-Python metadata.
The existing complete validator checks that workflow without inventing another tool.

## Known issues

- Python 3.15 acceptance is pending the hosted trial; no local 3.15 run is claimed.
- Python.org now lists 3.10 as end-of-life. Retaining compatibility does not
  provide upstream security maintenance; prefer maintained interpreters for new use.
- Test coverage does not promise compatibility with unreleased interpreters,
  every implementation, free-threaded builds, or untested platforms.
- Ubuntu image patches and build dependencies remain floating. Windows live
  execution, tagged releases, and package-index publication remain absent.
- The external CI starter still chooses Python 3.11 and its own documented scope.

## Decisions

- Extend interpreter coverage without mixing in the upcoming Ubuntu alias change.
- Keep the compatibility floor and its strict fallback tests; do not silently
  convert an upstream support change into a package minimum-version change.
- Retain the extension only after the same full validator passes the trial.
  Investigate a failure without broadening runtime scope or weakening assertions.

## Validation

- Warning-strict local Python 3.11 baseline passed the complete portfolio.
- Workflow syntax/matrix shape and diff checks precede trial publication.
- A green hosted run is required before updating current compatibility guidance.

## Recommended next steps

1. Inspect the Python 3.15 hosted result and interpreter/setup logs.
2. If green, update current CI/install guidance with evidence and lifecycle limits.
3. Retain the November 5 platform review; do not infer a platform upgrade from this trial.

No human input is required.

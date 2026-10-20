# Product lab status

## Current direction

Ship a narrow WheelContract correctness patch: schema_version must be the
actual TOML integer 1, not a boolean or float that Python compares equal to 1.
Invalid declarations fail before artifact work. Other product runtimes and
WheelContract's schema-v1/target-dependency boundaries remain unchanged.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six maintained products; GrammarCheck remains archived.
- Hosted compatibility remains Python 3.10–3.15 on Ubuntu 24.04.
- WheelContract advances from 1.0.5 to 1.0.6 for a reproduced validation defect.
- Existing unit/self-contract suites gain focused regressions. No new schema,
  dependency resolver, replay, or mandatory release gate was added.
- The November 5 platform-policy review remains separate.

## Work today (2026-10-20, started 08:23 PDT)

- Started clean at synchronized ab20a6a. Inspected memory, Git/history,
  root/product docs, source/tests,
  active To-Sam, workflow/validator, and public GitHub. No active Sam note;
  MIT detected and baseline matrix 39274392555 green.
- Warning-strict baseline passed 140 product tests with one expected optional
  skip, reproducible builds, isolated installs, contracts, and wheel integrity.
- Reproduced full installed-fixture CLI false passes for schema_version = true
  and 1.0. Both parsers also accepted exponent 1e0 through numeric equality.
- Added a failing regression first, then required exact integer type/value
  before artifact settings. Invalid declarations get a precise setup error.
- Regression covers seven invalid values across standard/fallback parsers,
  positive integer forms, exit 2, empty stdout, and no artifact runner.
- Added boolean/float fixtures to the existing installed self-contract. Their
  invalid artifact paths must not be reached by the packaged checker.
- Updated runtime/package version, product/current release claims, root README
  and product index. Public exact-source installation passed; install, pipx,
  checkout, and external-CI consumer pins now select correction revision 18a6492.

## Changes since the prior run

The prior run improved ProofRun diagnosis and exports. This run uses the frozen
product correctness exception for a reproduced WheelContract validation defect;
it does not add another example or guide for symmetry.

## External-user value

Malformed version declarations no longer silently select schema v1 or trigger
artifact build/install/case execution. Valid integer-v1 contracts retain their
existing behavior, and invalid declarations receive an actionable setup error.

## Known issues

- This patch changes only WheelContract's version discriminator, not general
  TOML validation across other frozen products.
- Python 3.10's dependency-free parser retains its documented subset.
- Target dependencies remain unresolved; checker/project/target environments
  remain separate. Existing process and output bounds stay unchanged.
- Local focused evidence is Python 3.11/3.14 and Python 3.10 grammar. Hosted
  interpreter evidence is Ubuntu-only and does not establish Windows coverage.
- Consumer pins select the tested correction source, not build-dependency locks
  or a package-index release. Other five source selections remain unchanged.

## Decisions

- Apply the correctness exception only after real false-pass reproduction.
- Check type plus value; do not coerce malformed declarations or change schema.
- Keep JSON case numeric 1/1.0 equality intact: a version discriminator has a
  different type contract from asserted numeric output.
- Reuse existing tests/self-contract rather than add another release gate.

## Validation

- Regression failed before the fix and passed on Python 3.11/3.14 afterward.
- Modified source/test parse with Python 3.10 grammar. Full warning-strict
  revalidation passed 141 product tests (one expected optional skip), twelve
  reproducible builds, six installs, five installed self-contract cases,
  AgentScope behavior, release claims, and complete wheel integrity.
- Exact public-source identity/version and invalid/valid CLI acceptance passed,
  including both prebuilt and disposable-archive five-case self-contracts.
  Other products' runtime sources are unchanged.
- Scoped pipx installation of the same revision passed version and all five
  installed self-contract cases. Correction CI 39449248459 passed Python 3.10–3.15.
- All 71 local links/anchors and current pip/pipx/template pin checks passed.
- Final consumer-state warning-strict portfolio validation passed the same
  141 tests and all existing artifact/behavior/release checks. The original
  missing-command replay passed with the pinned installed 1.0.6 checker.

## Recommended next steps

1. Keep exact-source install/CI consumer pins aligned with demonstrated fixes.
2. Reproduce similar discriminator issues independently before changing another
   frozen product; do not infer correctness from this patch.
3. Retain the November 5 platform-policy review.

No human input is required.

# Product lab status

## Current direction

The six completed local MVPs remain the maintained portfolio and GrammarCheck
remains archived. The public five-version Portfolio CI matrix is green after
its first hosted run exposed test fixtures that depended on local Git and
Python behavior. No frozen product interface or runtime behavior changed.

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
- Installed ReleaseFact checks its existing seven portfolio claims plus one
  local three-claim runtime/README/STATUS contract for every maintained product.

## Completed today (2026-09-29)

- Audited the live public GitHub surface. The repository is public with a useful
  description and topics, but its only hosted Portfolio CI run failed on all
  five supported Python versions.
- Compared the hosted failure, the missing repository-level license signal, and
  source-only installation guidance. Selected CI because it was an observed
  correctness and trust failure on the current commit; the other two remain
  adoption opportunities.
- Traced four Python 3.11–3.14 failures to a ProofRun test repository inheriting
  Git's machine-specific default branch. The fixture now explicitly initializes
  `main`.
- Traced Python 3.10's earlier failure to a WheelFact strictness fixture using a
  TOML boolean outside the intentionally narrow fallback value subset. Changed
  it and the equivalent later ReleaseFact fixture to schema-relevant quoted
  unknown values, retaining the exact unsupported-key assertion.
- Added a Portfolio CI badge to the root README so visitors can see the hosted
  validation state directly.

## Changes since the prior run

Local validation previously hid two platform-dependent fixtures: this host
defaults new Git repositories to `main` and Python 3.11 uses the full standard
TOML parser. The tests are now deterministic across the hosted Git default and
Python 3.10 fallback path. The public README now exposes CI state. No product
API, schema, package version, or implementation changed.

## Known issues

- Hosted portfolio CI remains Ubuntu-only.
- GitHub does not currently detect a repository-level license because licenses
  exist only inside product directories.
- Product READMEs primarily document source-checkout usage; there is no release
  or package-index installation path.
- The archived GrammarCheck code uses CPython's documented best-effort target
  grammar and is not exact interpreter compatibility evidence.
- Standard setuptools sdists were not byte-reproducible across source copies in
  the prior rehearsal because tar member mtimes retained wall-clock state; the
  portfolio does not publish sdists.
- Local validation requires an interpreter with `setuptools>=77`; the default
  `python3` on this host fails that preflight, while `python3.11` passes.
- Internal `RECORD` consistency is not provenance, authenticity, or signature
  verification. WheelFact deliberately makes no such claim.
- Product-local ReleaseFact contracts intentionally cover only canonical
  runtime and frozen handoff claims; historical version examples are not
  release assertions.

## Decisions

- Fix the observed hosted matrix before starting a new product or onboarding
  experiment.
- Make Git fixture state explicit instead of depending on user or runner
  `init.defaultBranch` configuration.
- Keep strictness tests inside the declared value subset of each Python 3.10
  fallback parser; the tested behavior is unknown-key rejection, not general
  TOML conformance.
- Expose hosted validation in the README rather than making visitors discover
  the Actions page manually.

## Validation

- Pre-change warning-strict Python 3.11 portfolio validation passed all 133
  maintained tests with one expected skip, twelve reproducible builds, six
  installs, seven ReleaseFact contracts, all behavior contracts, and six wheel
  integrity checks, reproducing the local/hosted discrepancy.
- Post-change focused warning-strict suites pass: ProofRun 53 tests with one
  expected skip, WheelFact 9 tests, and ReleaseFact 5 tests.
- Direct calls to both Python 3.10 fallback parsers accept the replacement
  quoted fixture value. Final warning-strict Python 3.11 portfolio validation
  passes all 133 maintained tests with one expected skip, twelve reproducible
  builds, six installs, seven ReleaseFact contracts, all behavior contracts,
  and six wheel integrity checks. The four archived GrammarCheck tests, local
  Markdown targets, shell syntax, and diff checks also pass.
- The first repair commit made Python 3.11–3.14 hosted jobs green. Python 3.10
  then reached two additional ProofRun invalid-manifest subtests whose exact
  error wording differed between the fallback and standard TOML parsers. Their
  assertions now require the stable semantic fragments (`env` and
  `unsupported key`) shared by both paths.
- Hosted run 36663392744 passes on Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Recommended next steps

1. Confirm the latest pushed commit retains the green hosted matrix; treat any
   hosted-only failure as the next priority.
2. Compare a repository-level license for clear reuse terms, an honest
   install-from-Git quick start, and a fresh user-workflow gap.
3. Keep the six product schemas and command-line contracts frozen absent a
   demonstrated correctness or safety defect.

No human input is required.

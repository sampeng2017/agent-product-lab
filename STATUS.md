# Product lab status

## Current direction

The six completed local MVPs remain the maintained portfolio and GrammarCheck
remains archived. The public matrix is green and GitHub detects MIT. External
users now have a tested, source-pinned installation path for each maintained
tool plus first-use examples in their own repositories.

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
- `docs/INSTALLATION.md` documents six separate packages and their console
  commands, virtual environments, a tested public source revision, checkout
  installs, updates, and troubleshooting.

## Completed today (2026-10-01)

- Confirmed MIT detection and green Python 3.10–3.14 CI for `84e76fa`.
- Compared moving `main`, a pinned public revision, and checkout installs.
  Selected the validated full revision for the first-user path; documented
  development tracking separately without creating an unsupported release tag.
- Installed all six tools from real GitHub VCS requirements in a new Python 3.11
  environment with normal build isolation and no checkout import paths.
- Verified recorded source revisions, package names, versions, zero runtime
  requirements, and `pip check` on the installed tools.
- Rehearsed installed ProofRun preview/init/verify/validity/audit, AgentScope
  inspection/comparison, and a clean ResidueCheck command in a separate project.
- Added a shared installation guide, a task-oriented chooser, and installed-use
  entry points in the root README and all six product READMEs.

## Changes since the prior run

Previously, product docs assumed a source checkout and `PYTHONPATH`; several
showed console commands without explaining how to install them. Users can now
copy a package-specific Git requirement and run the tool in their own project.
The root starts with usefulness and installation before lab history. Package
versions, runtime behavior, schemas, and interfaces are unchanged.

## External-user value

Readers can choose by task, install one tool, preview their first verification,
and understand package-name versus command-name differences. A full public
revision keeps the chosen source stable while the lab continues developing.
The guide makes build-index access and source tracking explicit and explains
common environment, directory, and certificate failures.

## Known issues

- Hosted portfolio CI remains Ubuntu-only.
- There is no published tag or release. The guide pins the tested public
  `84e76fa` revision; maintainers must deliberately refresh it for future runtime
  changes. Source pinning does not pin build dependency versions.
- Windows activation is documented from Python's official instructions but was
  not executed on this macOS host; installed workflow rehearsal used Python 3.11.
- Hosted runners announced an `ubuntu-latest` migration beginning October 19;
  assess whether to pin the runner separately from this onboarding change.
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

- Use a tested full Git revision for onboarding. Pip's standard subdirectory
  syntax already supports this monorepo without a custom installer.
- Offer `main` with explicit upgrade guidance only for development tracking.
- Keep installation instructions centralized; each product links to its section
  and demonstrates the installed command before checkout development examples.
- No new installer, dependency, test framework, or release gate is needed for
  this documentation and adoption change.

## Validation

- Pre-change warning-strict Python 3.11 portfolio validation passed all 133
  maintained tests with one expected skip, twelve reproducible builds, six
  installs, seven ReleaseFact contracts, all behavior contracts, and six wheel
  integrity checks.
- Public run 36809212730 passes on Python 3.10, 3.11, 3.12, 3.13, and 3.14 at
  the inspected starting commit.
- The real VCS install and first-use rehearsal passed for the documented source
  revision. All six `direct_url.json` records confirm that exact commit and the
  expected subdirectory; no installed package declares runtime dependencies.
- Final warning-strict portfolio validation passed 133 tests with one expected
  skip, twelve reproducible builds, six installs, seven ReleaseFact contracts,
  all behavior contracts, and six integrity checks. All 43 edited-document
  local links and anchors passed, as did AgentScope's required tests, compilation,
  instruction inspection, shell syntax, and diff checks.

## Recommended next steps

1. Add a small worked example for an external user showing a useful failing
   result, how to interpret it, and the successful result after correction.
2. Assess the upcoming hosted runner migration and retain stable release
   evidence before October 19.
3. Keep the six product schemas and command-line contracts frozen absent a
   demonstrated correctness or safety defect.

No human input is required.

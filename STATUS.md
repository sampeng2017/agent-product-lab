# Product lab status

## Current direction

The six completed local MVPs remain the maintained portfolio and GrammarCheck
remains archived. The latest public five-version Portfolio CI matrix is green.
The repository now has one detectable root MIT license, removing the public
reuse ambiguity that remained when licenses existed only inside product
subdirectories. No frozen product interface or runtime behavior changed.

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

## Completed today (2026-09-30)

- Confirmed local `main`, `origin/main`, and the latest public workflow run all
  start at commit `49841aa`; hosted Python 3.10–3.14 jobs remain green.
- Audited the public GitHub metadata: the repository is public with a useful
  description and seven relevant topics, but GitHub reported no detectable
  license, no release, and no repository-level reuse terms.
- Compared a root license, install-from-Git onboarding, and a root product
  chooser against current GitHub and pip guidance.
- Added the same standard MIT text already used by the maintained product
  packages at the repository root and linked it from the public README.

## Changes since the prior run

Previously, GitHub's repository API returned `licenseInfo: null`, even though
every distributable product declared MIT and included a package-local license.
Visitors could inspect the code but had no repository-level permission covering
the lab documentation and shared validation files. The root now carries a
standard, detectable MIT license. No product API, schema, package version, or
implementation changed.

## Known issues

- Hosted portfolio CI remains Ubuntu-only.
- Product READMEs primarily document source-checkout usage; there is no release
  or package-index installation path.
- The public repository has no tag or release, so an install-from-Git quick
  start would either follow moving `main` or require an unpublished revision.
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

- Select the root license because missing reuse permission is more fundamental
  adoption friction than shortening an installation command or product list.
- Reuse the established product-wide MIT choice rather than inventing new
  terms; keep product-local copies so built artifacts remain self-contained.
- Do not add a license-synchronization gate: the root file is a public legal
  surface, while package-local notices intentionally retain their own holders.
- Defer install-from-Git onboarding until the repository documents whether
  users should track `main` or a stable tag/revision.

## Validation

- Pre-change warning-strict Python 3.11 portfolio validation passed all 133
  maintained tests with one expected skip, twelve reproducible builds, six
  installs, seven ReleaseFact contracts, all behavior contracts, and six wheel
  integrity checks.
- Public run 36663540623 passes on Python 3.10, 3.11, 3.12, 3.13, and 3.14 at
  the inspected starting commit.
- Final warning-strict Python 3.11 portfolio validation passes all 133
  maintained tests with one expected skip, twelve reproducible builds, six
  installs, seven ReleaseFact contracts, all behavior contracts, and six wheel
  integrity checks. The root license matches the established product text byte
  for byte; 25 local Markdown targets, shell syntax, and diff checks also pass.

## Recommended next steps

1. Confirm GitHub detects the pushed root license and the hosted matrix remains
   green; repair either public-surface regression before new work.
2. Decide whether external users should install from moving `main` or a stable
   tag/revision, then test and document one honest VCS quick start.
3. Keep the six product schemas and command-line contracts frozen absent a
   demonstrated correctness or safety defect.

No human input is required.

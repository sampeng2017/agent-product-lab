# Product lab status

## Current direction

The six completed local MVPs remain the maintained portfolio and GrammarCheck
remains archived. Portfolio validation now verifies each product's runtime and
frozen product-document version claims against canonical package metadata,
closing a release-drift gap without changing any frozen product interface.

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

## Completed today (2026-09-28)

- Passed the clean warning-strict Python 3.11 baseline: 133 maintained tests,
  one expected optional skip, twelve reproducible wheel builds, six isolated
  installs, all maintained contracts, and six wheel-integrity checks.
- Compared release-version consistency, full-validator residue wrapping, and
  local Markdown-link validation. Only release consistency reproduced a gap;
  the other two had no current failure and broader link behavior has mature
  ecosystem ownership.
- Built a disposable ProofRun wheel with runtime version 9.9.9 but package
  metadata 1.8.1. The existing `--help` smoke and WheelFact integrity gate both
  accepted it.
- Added narrow ReleaseFact contracts for the five products that lacked one and
  made portfolio validation check all six local contracts plus the existing
  portfolio contract through the installed artifact.
- Confirmed the new ProofRun contract rejects the mutation with drift exit 1
  and identifies the runtime claim while preserving the two matching document
  claims.

## Changes since the prior run

Previously only ReleaseFact had an explicit local contract tying source and
product documentation to package metadata. Every maintained product now has
the same three-claim release-drift check, and the root validator executes all of
them with the installed ReleaseFact artifact. No product API, schema, package
version, or implementation changed.

## Known issues

- Hosted portfolio CI remains Ubuntu-only, and the repository has no Git remote.
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

- Reuse ReleaseFact rather than adding shell comparisons or reopening its
  frozen schema; one canonical value per product matches schema v1 exactly.
- Keep local contracts to runtime, README, and STATUS release claims. The
  existing root contract remains responsible for portfolio-level ReleaseFact
  claims.
- Reject version drift before later installed behavior checks so diagnostics
  point directly to the inconsistent claim.

## Validation

- Pre-change `PYTHON_BIN=python3.11 PYTHONWARNINGS=error
  ./scripts/validate-portfolio.sh` passed 133 maintained tests with one expected
  skip and every installed contract.
- All six product-local contracts pass from source; the disposable ProofRun
  runtime mutation fails with exit 1 and one explicit drift.
- Final warning-strict Python 3.11 portfolio validation passes all 133 maintained
  tests with one expected skip, twelve byte-reproducible wheel builds, six
  isolated installs, seven ReleaseFact contracts, all installed behavior
  contracts, and six explicit integrity passes. Shell syntax, four archived
  GrammarCheck tests, 28 local Markdown targets, and diff checks also pass.

## Recommended next steps

1. Compare at least three fresh repository-grounded opportunities before
   changing a frozen product.
2. Favor a bounded experiment with a demonstrated local failure and an explicit
   abandonment gate; do not add more version claims without an independently
   drifting release surface.
3. Keep the six product schemas and command-line contracts frozen absent a
   demonstrated correctness or safety defect.

No human input is required.

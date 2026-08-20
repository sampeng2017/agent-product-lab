# Product lab status

## Current direction

Sam explicitly approved switching to a new idea on 2026-08-20. ProofRun is now
a preserved completed local MVP, not the active product. No replacement idea
has been selected yet.

## Portfolio shape

- `products/proofrun/` contains the complete ProofRun v1.8.1 implementation,
  tests, documentation, manifest, and example GitHub Actions workflow.
- `products/next-product/` is the clean workspace for the next idea.
- Root documentation coordinates the portfolio and future autonomous runs.

## Completed today

- Converted the repository from a single-product layout into a product lab.
- Moved all ProofRun-specific implementation and documentation into
  `products/proofrun/` without changing its code.
- Added a next-product workspace and explicit discovery/build instructions.
- Archived the optional ProofRun GitHub remote request because it is no longer
  an active blocker or priority.
- Validated ProofRun from its new directory and committed the reorganization.

## Changes since the prior run

The active objective changed from extending ProofRun to finding and building a
new product. ProofRun remains available as a frozen reference implementation;
future work should create a separate product rather than reshaping ProofRun.

## Known issues

- The next product is deliberately unselected; current opportunity research is
  required before implementation.
- ProofRun has no published remote or hosted CI validation, but those are
  deferred productization gaps rather than blockers for the pivot.
- Root-level CI is intentionally absent until the next product establishes its
  own runnable validation workflow.

## Decisions

- ProofRun v1.8.1 is considered a completed local MVP.
- Preserve ProofRun history and behavior; do not delete or silently reuse its
  package identity for the new product.
- Select the next idea using current evidence, not the original opportunity
  scan from ProofRun's first run.
- The next product must have a distinct user, problem statement, name, folder,
  implementation, tests, and run instructions.
- Prefer a small locally runnable wedge that does not require credentials for
  its first useful experience.

## Recommended next step

Follow `NEXT_RUN.md`: research at least three current opportunities, document
the comparison, select one, rename `products/next-product/` to the product slug,
and build the smallest useful tested prototype during the same run.

# Next run: select and start a new product

This file records Sam's explicit pivot instruction. It overrides the previous
default of continuing ProofRun.

## Required outcome

The next autonomous run must select and begin a genuinely new product. Do not
spend the run extending ProofRun unless its preserved MVP fails validation.

## Discovery process

1. Inspect root Git history, `README.md`, `STATUS.md`, `DAILY_LOG.md`, active
   `To-Sam/` messages, and the contents of `products/`.
2. Research at least three current software or service opportunities using
   recent primary or otherwise authoritative sources.
3. Record for each candidate: target user, painful job, existing alternatives,
   why now, smallest useful wedge, distribution path, and principal risk.
4. Compare the candidates explicitly and select one. Do not default to one of
   the original ProofRun-era candidates without fresh evidence.
5. Replace the placeholder `products/next-product/` directory with a stable,
   descriptive product slug.
6. Create product documentation containing the selection evidence, product
   promise, initial user, success signal, and near-term scope.
7. Build a runnable prototype plus proportionate automated validation in the
   selected product folder during the same run.
8. Update root `STATUS.md` and append `DAILY_LOG.md`; leave a clean descriptive
   commit and exact continuation instructions.

## Selection guardrails

- Prefer a frequent, specific problem over a broad platform idea.
- The first useful workflow should run locally without an account or secret.
- Avoid products whose value cannot be demonstrated with a small prototype.
- Keep ProofRun frozen under `products/proofrun/`; borrow patterns only when
  they naturally serve the new product.


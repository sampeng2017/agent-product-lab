# Next run: decide portfolio-wide wheel integrity coverage

GrammarCheck v0.1.0 remains archived. The six maintained products are frozen.
ReleaseFact v1.0.0 is now frozen as the fourth local MVP.
WheelFact v1.0.2 now verifies complete wheel `RECORD` membership, secure hashes,
and provided sizes before checking its unchanged exact schema-v1 contract.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, product handoffs, tests, and
the portfolio validator. Check Git state/history and rerun warning-strict
portfolio validation before editing.

## Bounded decision

1. Determine whether all six built wheels need a maintained integrity gate. The
   current installed WheelFact dogfood covers AgentScope and ResidueCheck; pip
   25.0.1 accepted all four disposable `RECORD` corruptions in the 2026-09-26
   experiment.
2. Compare three narrow options: exact WheelFact contracts for the remaining
   products, a contract-independent WheelFact mode, and a focused validator
   function using the product's tested core. Include maintenance and diagnostic
   cost, not only line count.
3. Retain a portfolio-wide gate only if it avoids duplicated expectations and
   keeps WheelFact's artifact-contract boundary clear. Otherwise document the
   negative result and compare at least three fresh repository-grounded product
   opportunities.

## Guardrails

- Do not reopen another frozen product without a demonstrated defect.
- Do not turn WheelFact into a general packaging linter, builder, installer,
  repair tool, policy engine, provenance checker, or signature verifier.
- Do not infer authenticity from internal `RECORD` consistency.
- Do not retain a helper whose value is equivalent to a short transparent
  standard-library assertion in the single portfolio validator.

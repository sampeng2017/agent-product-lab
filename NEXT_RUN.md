# Next run: select a fresh bounded opportunity

GrammarCheck remains archived. The six maintained products are frozen.
ReleaseFact v1.0.0 is now frozen as the fourth local MVP.
WheelFact v1.0.3 now provides contract-independent integrity coverage for all
six built wheels while retaining exact contracts for ResidueCheck and
AgentScope.
ReleaseFact now checks local runtime and frozen product-document version claims
for every maintained product in addition to its portfolio-wide claims.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, product handoffs, tests, the
workflow, and the portfolio validator. Check Git state/history and rerun
warning-strict portfolio validation before editing.

## Bounded decision

1. Identify at least three fresh opportunities from concrete repository or
   validation evidence. Name existing ecosystem ownership and the smallest
   useful experiment for each.
2. Select at most one opportunity. Reproduce its failure or costly manual step
   before retaining implementation.
3. Define an abandonment gate up front. Prefer a transparent repository-local
   check over a new product when both provide equivalent evidence.

## Guardrails

- Do not reopen a frozen product without a demonstrated correctness or safety
  defect.
- Do not add release gates that duplicate reproducible builds, exact artifact
  contracts, installed behavior contracts, release-fact checks, or complete
  wheel `RECORD` integrity.
- Do not treat internal wheel consistency as provenance or authenticity.
- Keep each product's three-claim release contract narrow; add a claim only when
  a real release surface can drift independently of package metadata.
- Keep credentialed services, publishing, mutation, repair, and broad policy
  engines out of the first experiment.

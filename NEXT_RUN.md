# Next run: reassess adoption and runner stability

GrammarCheck remains archived. The six maintained products are frozen.
ReleaseFact v1.0.0 is now frozen as the fourth local MVP.
WheelFact v1.0.3 now provides contract-independent integrity coverage for all
six built wheels while retaining exact contracts for ResidueCheck and
AgentScope.
ReleaseFact now checks local runtime and frozen product-document version claims
for every maintained product in addition to its portfolio-wide claims.
The 2026-09-29 run repaired two portable-test fixtures after the first public
Portfolio CI run failed across its matrix. The root README now shows CI state.
The 2026-09-30 run added the repository-level MIT license that GitHub previously
could not detect while licenses existed only inside product directories.
The 2026-10-01 run added tested installation commands pinned to public revision
`84e76fa` and examples that work in the user's own repository. The root and each
maintained product now link to `docs/INSTALLATION.md`.
The 2026-10-02 run added `examples/proofrun-stale-proof/`: a temporary-repository
replay and guide that demonstrate valid evidence, a stale status after an edit,
and restored validity after fresh verification with the frozen installed tool.
The 2026-10-03 run added `examples/agentscope-rule-scope/`, which diagnoses a
misdirected API instruction pattern, corrects its scope in a temporary copy,
and distinguishes informational coverage from an intended-target policy gate.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, product handoffs, tests, the
workflow, and the portfolio validator. Check Git state/history, inspect the
latest public GitHub matrix and license result, and rerun warning-strict
portfolio validation before editing.

## Bounded decision

1. If GitHub does not detect the root MIT license or a hosted matrix job fails,
   repair that public surface before new work.
2. Otherwise compare artifact-release onboarding, the approaching hosted runner
   migration, and a fresh user-workflow improvement. Prioritize concrete gaps
   over producing another example for symmetry.
3. Define an abandonment gate up front. Do not advertise package-index or
   release availability that the repository does not provide.

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
- Keep root and package-local license copies: the former communicates repository
  reuse terms, while the latter keeps built artifacts self-contained.
- Change any installation promise only with an honest, tested path. Preserve the
  documented public revision unless a newly tested runtime change warrants
  updating it.
- Assess the announced October 19 hosted runner migration independently; do
  not mix an untested platform switch into a worked-example change.
- Preserve the ProofRun replay as an external-user example, not a new product
  or a mandatory internal release gate.
- Preserve the AgentScope replay's explicit modeled profile and policy scope;
  intentional ignored rules are not automatically defects.

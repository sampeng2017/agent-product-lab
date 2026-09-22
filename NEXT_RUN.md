# Next run: select the seventh bounded experiment

WheelFact v1.0.0, ResidueCheck v1.0.0, ReleaseFact v1.0.0, WheelContract v1.0.0,
AgentScope v1.0.0, and ProofRun v1.8.1 are frozen local MVPs.
ReleaseFact v1.0.0 is now frozen as the fourth local MVP.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, and the portfolio validator.
Check Git status/history and rerun warning-strict portfolio validation before
editing.

## Completed release

WheelFact checks existing wheels against exact distribution metadata, console
scripts, and non-`.dist-info` payload members. ResidueCheck and AgentScope each
produce nine passing facts without installation. The deliberately stale
AgentScope rehearsal reported four scalar, two console-script, and two member
mismatches in one run without changing schema v1.

The 16-line contract was clearer than a 44-line focused comparison script that
still omitted safe archive selection, bounds, strict parsing, and setup-error
semantics. WheelFact was promoted unchanged to v1.0.0 and frozen.

## Bounded next selection

1. Identify at least three current software-product opportunities grounded in
   repository friction or a clearly adjacent workflow.
2. Verify current ecosystem context with authoritative sources and record why
   existing tools do or do not already own each problem.
3. Select one smallest useful wedge with an explicit retention/abandonment test.
4. Build and validate a runnable prototype in a stable product directory during
   the same run; do not stop at research or planning.

## Guardrails

- Do not reopen a frozen product unless validation demonstrates a correctness
  or safety defect.
- Avoid overlapping ProofRun verification receipts, AgentScope instruction
  discovery, WheelContract installed behavior, ReleaseFact version claims,
  ResidueCheck filesystem residue, or WheelFact exact wheel structure.
- Keep the experiment local-first, dependency-light, bounded, and independently
  useful; abandon it if a focused transparent script is clearer.

# Next run: ReleaseFact release rehearsal

ProofRun v1.8.1, AgentScope v1.0.0, and WheelContract v1.0.0 are frozen local
MVPs. ReleaseFact v0.1.0 is the active retained prototype.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, and the complete ReleaseFact
implementation/tests/docs. Check Git status/history and rerun the warning-strict
portfolio validator before editing.

## Bounded next experiment

Exercise a ReleaseFact version bump in a disposable copy of the repository:

1. Change only the canonical version and capture the seven-claim drift report.
2. Follow that report to update the declared claims, then confirm a clean pass.
3. Record whether any diagnostic is ambiguous, redundant, or missing.
4. Add behavior only for a reproduced gap. If the contract already guides the
   release cleanly, keep schema v1 unchanged and focus on release-readiness.

## Guardrails

- Do not mutate this checkout merely to simulate drift; use a disposable copy.
- Do not reopen the three frozen products unless validation reveals a defect.
- Do not add regexes, recursive discovery, automatic rewriting, historical
  version inference, or a general configuration-synchronization surface.
- Keep ReleaseFact read-only and preserve exit 0/1/2.

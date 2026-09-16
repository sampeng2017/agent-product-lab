# Next run: ReleaseFact bounded prototype

WheelContract v1.0.0, AgentScope v1.0.0, and ProofRun v1.8.1 are frozen local
MVPs.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and `products/NEXT_PRODUCT_OPPORTUNITIES.md`. Check Git status/history
and rerun the warning-strict portfolio validator before editing.

## Bounded experiment

Prototype `products/releasefact/` as a read-only checker for one demonstrated
problem: a canonical version in `pyproject.toml` disagrees with explicit current
version claims in selected source, contract, or documentation files.

1. Start with a fixture modeled on the stale WheelContract v0.1.0 portfolio
   claim discovered during the 2026-09-15 release audit.
2. Support one canonical TOML value and explicit, deterministic file claims;
   report every mismatch in one run and distinguish invalid setup from drift.
3. Compare the manifest and diagnostics with a focused `rg`/shell equivalent.
4. Retain the product only if it materially improves clarity or complete
   diagnosis. Otherwise document the negative result and select another narrow
   opportunity.

## Guardrails

- Do not reopen the three frozen products unless validation reveals a defect.
- Do not auto-edit files, infer historical version mentions, publish artifacts,
  or become a general regex/config synchronization engine.
- Prefer a disposable fixture before dogfooding on repository files.
- Keep the prototype dependency-free and credential-free.

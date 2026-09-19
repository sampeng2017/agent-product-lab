# Next run: ResidueCheck real-build dogfood

ReleaseFact v1.0.0 is now frozen as the fourth local MVP.
ProofRun v1.8.1, AgentScope v1.0.0, and WheelContract v1.0.0 remain frozen.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, and the portfolio validator.
Check Git status/history and rerun warning-strict portfolio validation before
editing.

## Completed experiment

The ReleaseFact audit exposed a concrete blind spot: direct wheel builds updated
ignored `*.egg-info/` directories while ordinary Git status stayed clean.
ResidueCheck v0.1.0 now demonstrates a reusable bounded detector and reports all
three ignored-file change kinds in a disposable fixture. The prototype is
retained because it centralizes safe traversal, hashing, comparison, output
bounds, and failure handling that focused portable shell must rebuild.

## Bounded next experiment

1. Copy one portfolio product into a disposable directory and run its real PEP
   517 wheel build under the installed ResidueCheck prototype.
2. Measure the included entry/byte scope and elapsed overhead, and confirm the
   report names expected `build/` and `*.egg-info/` residue.
3. Repeat from the already-dirty disposable tree to exercise modified residue,
   then decide whether output remains useful without glob exclusions.
4. Add behavior only for a demonstrated diagnostic or safety gap. Otherwise
   promote/freeze the narrow surface if packaging and Python 3.10 audits pass.

## Guardrails

- Do not reopen ProofRun merely to absorb the product; its Git-state proof
  model is frozen and intentionally has different semantics.
- Do not build a sandbox, filesystem watcher, or general task runner.
- Do not recursively hash dependency/vendor trees without explicit bounds or
  exclusions.
- Keep all four completed product behaviors frozen unless validation reveals a
  concrete defect.

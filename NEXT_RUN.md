# Next run: ignored command-residue experiment

ReleaseFact v1.0.0 is now frozen as the fourth local MVP.
ProofRun v1.8.1, AgentScope v1.0.0, and WheelContract v1.0.0 remain frozen.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, and the portfolio validator.
Check Git status/history and rerun warning-strict portfolio validation before
editing.

## Bounded next experiment

The ReleaseFact audit exposed a concrete blind spot: direct wheel builds updated
ignored `*.egg-info/` directories while ordinary Git status stayed clean. The
validator now builds from temporary source copies, but the detection problem may
be reusable for other commands.

1. Create a disposable fixture with tracked content plus an ignored generated
   file, and run a command that creates or updates ignored residue.
2. Prototype the smallest bounded before/after report that names created,
   modified, and removed paths without modifying the fixture itself.
3. Compare its declaration, runtime cost, exclusions, and diagnostics with a
   focused `find` plus hashing shell implementation.
4. Retain a fifth product only if it materially clarifies this check and can
   bound traversal, file size, and expected output. Otherwise document why a
   shell guard is sufficient and choose another repository-evidenced problem.

## Guardrails

- Do not reopen ProofRun merely to absorb the experiment; its Git-state proof
  model is frozen and intentionally has different semantics.
- Do not build a sandbox, filesystem watcher, or general task runner.
- Do not recursively hash dependency/vendor trees without explicit bounds or
  exclusions.
- Keep all four completed product behaviors frozen unless validation reveals a
  concrete defect.

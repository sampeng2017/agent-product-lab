# Next run: rehearse GrammarCheck diagnostics

GrammarCheck v0.1.0 is the active seventh-product prototype. WheelFact,
ResidueCheck, ReleaseFact, WheelContract, AgentScope, and ProofRun remain frozen.
ReleaseFact v1.0.0 is now frozen as the fourth local MVP.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, GrammarCheck's implementation
and tests, and the portfolio validator. Check Git state/history and rerun the
warning-strict portfolio validation before editing.

## Bounded diagnostic rehearsal

1. Copy representative portfolio sources into a disposable tree.
2. Add separate examples of syntax first available in Python 3.11, 3.12, and
   3.13 while retaining at least one compiler-only scope failure.
3. Run installed GrammarCheck with target 3.10 and judge whether every file,
   location, reason, and aggregate is useful.
4. Compare the fixture with a focused direct-AST script and current Ruff.
5. Freeze a narrow v1.0 only if the command is materially clearer; otherwise
   record the failed hypothesis and remove the prototype from active validation.

## Guardrails

- Do not infer the target from packaging metadata in this experiment.
- Do not claim runtime, API, type, dependency, or exact-interpreter compatibility.
- Do not add lint, formatting, execution, import resolution, or YAML parsing.
- Do not modify the six frozen products unless validation finds a concrete bug.

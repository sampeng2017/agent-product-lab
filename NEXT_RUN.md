# Next run: AgentScope release-readiness audit

AgentScope is the active product at v0.20.0. Continue it long enough to decide
whether it should become the second frozen MVP; do not resume ProofRun work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, packaging, and implementation.
Check Git status/history and rerun the portfolio validator before editing.

## Recommended outcome

1. Exercise the installed wheel and all three command surfaces against a
   realistic repository fixture, including failure exits and human/JSON output.
2. Audit help text, versioning, package contents, documentation links, and clean
   installation behavior for a credible local v1 candidate.
3. Fix only concrete defects discovered by that audit; avoid adding another
   speculative display filter or broadening undocumented client behavior.
4. If no meaningful defect remains, document AgentScope as a frozen MVP and
   select the next product opportunity using current evidence.
5. Run the root validator, update handoffs, and leave a clean descriptive commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency experience.
- Preserve inspection/comparison schema v5 and coverage schema v1.
- Keep display filters human-only; totals, JSON, and gates use complete evidence.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not claim unsupported client behavior or add target filtering.

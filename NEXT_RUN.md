# Next run: define missing-guidance comparison semantics

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Evaluate and, if the contract is clear, add a missing-guidance policy for
profile comparison.

1. Decide whether missing means neither profile has applied guidance or whether
   each profile must have guidance; document the user and CI consequence before
   implementing it.
2. Prefer semantics that do not turn intentional profile-specific coverage into
   a redundant divergence failure.
3. If added, compose the gate with all existing comparison policies after full
   human or JSON rendering, with multi-target and empty-repository tests.
4. Preserve inspection schema v5 and comparison schema v4 unless the published
   result object genuinely needs new data.
5. Run the root portfolio validator plus focused AgentScope checks, update all
   handoffs, and leave a clean descriptive commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency first experience.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not broaden the frontmatter parser or claim undocumented client behavior.
- Preserve comparison schema v4 unless its published object contract changes.
- Preserve the root CI matrix and temporary-output package smoke tests.

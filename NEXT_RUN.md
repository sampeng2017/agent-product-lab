# Next run: expose cross-profile instruction divergence

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Add a comparison workflow that inspects the same targets under both supported
profiles and makes divergent applied source sets obvious.

1. Define a stable comparison model separate from presentation.
2. Add a `compare` CLI surface with concise human output and versioned JSON.
3. Include sources unique to each profile and sources common to both.
4. Add an optional nonzero gate for divergence without changing informational
   default exit behavior.
5. Cover nested `AGENTS.md`, proprietary instruction formats, unmatched
   path-specific files, multiple targets, and empty guidance.
6. Dogfood the command on a disposable fixture, update docs/status/log, validate,
   and leave a clean descriptive commit.

## Guardrails

- Preserve the read-only, zero-runtime-dependency first experience.
- Keep every modeled client behavior explicit and source-grounded.
- Do not broaden frontmatter parsing in the same change unless comparison is
  already complete and fully tested.
- Keep ProofRun frozen unless its preserved MVP fails validation.

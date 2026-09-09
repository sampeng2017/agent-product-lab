# Next run: evaluate display-only coverage filtering

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Evaluate whether a source-dense modular coverage report benefits from an
optional presentation filter after v0.18.0 bounded target width.

1. Use a fixture with many modular sources, mixed states, and nested discovery.
2. Prefer a repeatable source-path selector only if it materially reduces noise.
3. Make filtering explicitly display-only: ignored/invalid gates must evaluate
   the complete unfiltered coverage result so a hidden source cannot pass CI.
4. Preserve caller target order, source discovery order, full legends, detailed
   reasons, schema-v1 JSON, and the 12-column compact chunks.
5. Do not add target filters; callers already select targets positionally.
6. Run the root validator and focused checks, update handoffs, and leave a clean
   descriptive commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency first experience.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not broaden the frontmatter parser or claim undocumented client behavior.
- Preserve inspection/comparison schema v5 and coverage schema v1.
- Preserve all existing evidence categories, discovery semantics, and exits.
- Preserve the root CI matrix and temporary-output package smoke tests.

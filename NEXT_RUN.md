# Next run: evaluate occurrence-state coverage filtering

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Evaluate whether source-dense coverage reports benefit from a display-only
occurrence-state selector after v0.19.0 source-path filtering.

1. Use mixed matched, ignored, invalid, and not-discovered evidence.
2. Prefer a selector only if it makes gate failures materially faster to scan.
3. Keep filtering human-only and presentation-only: aggregate counts and every
   ignored/invalid gate must evaluate the complete unfiltered result.
4. Define source-level selection clearly when one source has mixed outcomes.
5. Preserve discovery/caller order, detailed reasons, compact chunks, full
   legends, the public API, and complete coverage schema-v1 JSON.
6. Do not add target filters; callers already select targets positionally.
7. Run the root validator and focused checks, update handoffs, and leave a clean
   descriptive commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency first experience.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not broaden the frontmatter parser or claim undocumented client behavior.
- Preserve inspection/comparison schema v5 and coverage schema v1.
- Preserve all existing evidence categories, discovery semantics, and exits.
- Preserve the root CI matrix and temporary-output package smoke tests.

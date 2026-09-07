# Next run: dogfood modular coverage at scale

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Exercise `agentscope coverage` against a realistic repository with multiple
modular sources and a representative target set, then make one evidence-backed
usability improvement if needed.

1. Evaluate whether the vertical source/occurrence output stays scannable for a
   larger source-by-target set.
2. If it does not, prefer an explicit compact-table option or narrow source/path
   filters; keep the default schema-v1 JSON stable.
3. Preserve caller target order, first-discovery source order, and the distinction
   between not discovered, ignored, matched, and invalid.
4. Do not imply that every modular rule should match every requested target;
   `--fail-on-ignored-sources` must remain an explicit strict policy.
5. Keep standard sources, references, duplicates, and `agents-md` shadows out of
   modular coverage unless real usage demonstrates a clear need.
6. Run the root portfolio validator plus focused AgentScope checks, update all
   handoffs, and leave a clean descriptive commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency first experience.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not broaden the frontmatter parser or claim undocumented client behavior.
- Preserve applied-path divergence, evidence categories, all existing gates, and
  inspection/comparison schema v5.
- Preserve coverage schema v1 unless a breaking contract change is justified.
- Preserve the root CI matrix and temporary-output package smoke tests.

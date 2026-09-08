# Next run: validate compact coverage at real scale

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Exercise `agentscope coverage --compact` against a real repository with many
modular sources and representative target paths, then improve it only if a
specific scaling problem appears.

1. Check matrix width, long paths, and higher-cardinality sets while retaining
   mixed matched, ignored, invalid, and not-discovered cells.
2. Compare the compact overview with the default reason-bearing view; keep each
   format's role clear rather than merging them.
3. If horizontal growth is genuinely troublesome, prefer deterministic column
   chunking before adding source/path filtering with ambiguous gate semantics.
4. Preserve caller target order, first-discovery source order, full legends,
   schema-v1 JSON, and all current policy exits.
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

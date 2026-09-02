# Next run: add a narrow comparison reference gate

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Add policy parity for invalid references in profile comparison.

1. Add `compare --fail-on-invalid-references` using the comparison schema-v4
   counts and ordered diagnostics already introduced in v0.11.0.
2. Keep it narrower than `--fail-on-invalid-sources` and compose all comparison
   gates with OR semantics after rendering complete human or JSON output.
3. Cover invalid imports, malformed non-reference sources, multiple targets,
   and composition with divergence in focused CLI tests.
4. Update the source-linked reference contract without changing discovery,
   applied-path divergence, or inspection schema v5.
5. Run the root portfolio validator plus focused AgentScope checks, update all
   handoffs, and leave a clean descriptive commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency first experience.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not broaden the frontmatter parser or claim undocumented client behavior.
- Preserve comparison schema v4 unless its published object contract changes.
- Preserve the root CI matrix and temporary-output package smoke tests.

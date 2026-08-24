# Next run: diagnose malformed path instructions

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Make unsupported or malformed path-instruction frontmatter distinguishable from
a valid instruction file that simply does not match the target.

1. Define source-grounded outcomes for missing frontmatter delimiters, missing
   `applyTo`, empty scalar values, YAML list values, and syntax outside the
   supported subset.
2. Emit precise ordered diagnostics without adding a runtime YAML dependency.
3. Preserve valid scalar matching, the v0.2.1 executable glob matrix, and
   recursive reference behavior.
4. Decide whether `--fail-on-invalid-references` should remain narrow or be
   complemented by a broader invalid-source policy; do not silently broaden its
   existing contract.
5. Version output only if its document shape changes, and document migration.
6. Update docs/status/log, validate both products, and leave a clean descriptive
   commit.

## Guardrails

- Preserve the read-only, zero-runtime-dependency first experience.
- Keep every modeled client behavior explicit and source-grounded.
- Keep inspection schema v2 and comparison schema v1 stable unless a documented
  additive field is necessary.
- Keep both inspection gates informational by default and retain exit 2 for
  invalid repository arguments.
- Keep ProofRun frozen unless its preserved MVP fails validation.

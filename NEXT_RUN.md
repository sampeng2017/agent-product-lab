# Next run: make invalid references enforceable

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Turn v0.3.0's invalid `@` reference diagnostics into an opt-in CI policy without
making ordinary inspection fail.

1. Add `--fail-on-invalid-references` to inspection with a precise exit 1
   contract; invalid repository arguments must remain exit 2.
2. Add aggregate and per-target invalid-reference counts to JSON. Version the
   inspection schema if its shape changes and document migration explicitly.
3. Make human output summarize invalid-reference counts without hiding the
   ordered source-level reasons.
4. Decide and test how the new gate composes with `--require-instructions` and
   multiple targets.
5. Preserve comparison semantics, glob behavior, and reference resolution.
6. Update docs/status/log, validate both products, and leave a clean descriptive
   commit.

## Guardrails

- Preserve the read-only, zero-runtime-dependency first experience.
- Keep every modeled client behavior explicit and source-grounded.
- Keep scalar frontmatter and the v0.2.1 glob compatibility matrix unchanged.
- Keep v0.3.0 reference parsing and containment behavior unchanged unless a
  regression is found.
- Keep ProofRun frozen unless its preserved MVP fails validation.

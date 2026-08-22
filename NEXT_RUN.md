# Next run: explain supported instruction references

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Model Copilot CLI's documented `@` references in the instruction files where
they are supported, while keeping scope inspection read-only and explainable.

1. Capture the current source rules for relative imports, nested imports,
   supported file types, and containment.
2. Define how referenced files appear in human and JSON inspection results
   before implementation; version schemas only if their shape changes.
3. Resolve references recursively with cycle, depth, missing-file, and
   repository-escape diagnostics.
4. Do not expand references from `GEMINI.md` or `*.instructions.md`, matching the
   documented Copilot CLI boundary.
5. Preserve glob matching, comparison semantics, and both policy gates.
6. Update docs/status/log, validate both products, and leave a clean descriptive
   commit.

## Guardrails

- Preserve the read-only, zero-runtime-dependency first experience.
- Keep every modeled client behavior explicit and source-grounded.
- Keep scalar frontmatter and the v0.2.1 glob compatibility matrix unchanged.
- Keep ProofRun frozen unless its preserved MVP fails validation.

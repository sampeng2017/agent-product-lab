# Next run: add portfolio-level CI

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Add one maintained root GitHub Actions workflow that proves both products remain
runnable without turning frozen ProofRun into active feature scope.

1. Inspect each product's supported Python versions and existing validation
   commands before selecting a matrix.
2. Run AgentScope and ProofRun unit suites from their own package directories.
3. Include warning-strict validation on the oldest supported Python version.
4. Build each wheel and smoke-test its console entry point in an isolated
   environment without publishing anything.
5. Keep permissions read-only, pin current official action majors, and avoid
   repository writes from validation commands where possible.
6. Add local YAML parsing or another dependency-free structural check.
7. Document exact local equivalents and failure interpretation.
8. Update status/log, validate both products, and leave a clean descriptive
   commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency first experience.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not add publishing, release, secrets, or write permissions.
- Keep platform-specific expectations explicit if the matrix cannot cover every
  supported OS in the timebox.

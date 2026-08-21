# Next run: harden path-specific glob compatibility

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Make the `copilot-cli` profile's scalar `applyTo` matcher conform to GitHub's
documented path semantics within the syntax subset AgentScope claims.

1. Capture a source-linked compatibility matrix for anchored paths, nested
   segments, `*`, `**`, `?`, and comma-separated patterns.
2. Add table-driven tests before changing matching behavior.
3. Fix mismatches without adding a runtime dependency or broadening YAML parsing.
4. Confirm inspection and comparison JSON schemas and both policy gates remain
   stable.
5. Dogfood matching and comparison on representative planned and existing paths.
6. Update docs/status/log, validate both products, and leave a clean descriptive
   commit.

## Guardrails

- Preserve the read-only, zero-runtime-dependency first experience.
- Keep every modeled client behavior explicit and source-grounded.
- Do not broaden frontmatter parsing to YAML lists or add `@` references in the
  same change; keep the matcher change independently reviewable.
- Keep ProofRun frozen unless its preserved MVP fails validation.

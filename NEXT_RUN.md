# Next run: complete Copilot repository discovery

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Close the highest-value repository-scoped discovery gaps against GitHub's
current Copilot CLI documentation.

1. Recheck the cited official discovery rules and define the exact standard
   locations and traversal order AgentScope will model.
2. Add `.claude/CLAUDE.md` and any other clearly documented repository-local
   locations missing from the current profile.
3. Specify ordering and deduplication when equivalent files are reachable by
   more than one discovery route.
4. Preserve recursive-reference boundaries, path-frontmatter diagnostics, and
   all existing policy exits.
5. Keep user-level locations out of scope unless a repository-independent input
   can be modeled safely and explicitly in the same timebox.
6. Update docs/status/log, validate both products, and leave a clean descriptive
   commit.

## Guardrails

- Preserve the read-only, zero-runtime-dependency first experience.
- Keep every modeled client behavior explicit and source-grounded.
- Keep inspection schema v3 and comparison schema v1 stable unless a documented
  additive field is necessary.
- Keep inspection informational by default and retain exit 2 for invalid
  repository arguments.
- Keep ProofRun frozen unless its preserved MVP fails validation.

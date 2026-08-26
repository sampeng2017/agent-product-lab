# Next run: model the Copilot session directory

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Close the remaining ambiguity between AgentScope's target-based discovery and
GitHub's documented live-session discovery.

1. Recheck the cited official standard-location and modular-location rules.
2. Add an explicit repository-contained session-directory input (for example,
   `--cwd`) without changing the process working directory or reading external
   state implicitly.
3. Model repository root, session directory, intermediate directories, and
   target-nested directories separately; exclude modular instruction trees from
   intermediate-only locations as GitHub documents.
4. Preserve v0.6.0 root-to-target behavior when the session directory is the
   repository root, including first-resolved-source deduplication.
5. Cover divergent session/target branches, planned targets, containment,
   ordering, JSON stability, and comparison behavior.
6. Keep user-level and environment-configured directories out of scope unless
   they can be modeled explicitly and safely in the remaining timebox.
7. Update docs/status/log, validate both products, and leave a clean descriptive
   commit.

## Guardrails

- Preserve the read-only, zero-runtime-dependency first experience.
- Keep every modeled client behavior explicit and source-grounded.
- Keep inspection schema v3 and comparison schema v1 stable unless a documented
  additive field is necessary.
- Keep inspection informational by default and retain exit 2 for invalid
  repository arguments.
- Keep ProofRun frozen unless its preserved MVP fails validation.

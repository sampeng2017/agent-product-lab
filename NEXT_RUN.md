# Next run: explain identical Copilot instruction copies

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Close the remaining gap between resolved-file deduplication and GitHub's
documented removal of identical instruction copies.

1. Recheck the cited official duplicate-copy rule and define exactly which
   standard source kinds participate.
2. Detect byte-identical or normalized-content copies without hiding distinct
   paths that happen to share only partial content.
3. Explain the first retained source and later duplicate sources in human and
   JSON output; do not silently erase useful provenance.
4. Preserve current resolved-path and symlink deduplication, immediate reference
   expansion, session-aware ordering, and modular-path diagnostics.
5. Cover copies across repository root, intermediate, session, target-nested,
   and divergent branches, plus interaction with references.
6. Keep user-level and environment-configured directories out of scope unless
   they can be modeled explicitly and safely in the remaining timebox.
7. Update docs/status/log, validate both products, and leave a clean descriptive
   commit.

## Guardrails

- Preserve the read-only, zero-runtime-dependency first experience.
- Keep every modeled client behavior explicit and source-grounded.
- Version JSON only when its serialized shape actually changes.
- Keep inspection informational by default and retain exit 2 for invalid
  repository arguments.
- Keep ProofRun frozen unless its preserved MVP fails validation.

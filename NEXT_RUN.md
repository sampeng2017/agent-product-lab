# Next run: retain non-applied comparison evidence

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Preserve useful non-applied evidence when comparing profiles.

1. Decide which states belong in comparison: `ignored`, `duplicate`, and
   `shadowed` are the current candidates; keep invalid evidence separate.
2. Preserve deterministic per-profile order and explain why each source did not
   apply without changing applied-path divergence semantics.
3. Update human and JSON output together; bump comparison schema v4 only if the
   result object gains fields.
4. Cover matched and unmatched modular rules, content duplicates, nested
   `AGENTS.md` shadowing, and multi-target ordering.
5. Run the root portfolio validator plus focused AgentScope checks, update all
   handoffs, and leave a clean descriptive commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency first experience.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not broaden the frontmatter parser or claim undocumented client behavior.
- Keep missing guidance defined as no applied source across any compared
  profile; do not silently turn it into a profile-parity rule.
- Preserve the root CI matrix and temporary-output package smoke tests.

# Next run: evaluate modular-rule coverage output

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Evaluate a compact source-oriented view of modular instruction coverage across
multiple requested targets.

1. Decide whether this belongs in a `coverage` subcommand or an explicit output
   option; keep existing inspection and comparison output unchanged by default.
2. Group each discovered `*.instructions.md` source with its matched, ignored,
   and invalid target occurrences while preserving caller target order.
3. Avoid implying that every modular rule must match every target; the existing
   `--fail-on-ignored-sources` gate remains the explicit strict policy.
4. Keep duplicate, shadowed, referenced, and standard sources outside the
   modular coverage matrix unless a clear use case justifies them.
5. Cover shared sources, target-specific discovery, planned targets, invalid
   frontmatter, multiple profiles where relevant, and stable human/JSON output.
6. Run the root portfolio validator plus focused AgentScope checks, update all
   handoffs, and leave a clean descriptive commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency first experience.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not broaden the frontmatter parser or claim undocumented client behavior.
- Keep comparison guidance defined as no applied source across any compared
  profile; do not silently turn it into a profile-parity rule.
- Preserve applied-path divergence, evidence categories, and all current policy
  gates.
- Preserve the root CI matrix and temporary-output package smoke tests.

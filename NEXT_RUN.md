# Next run: evaluate an ignored-path policy

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Evaluate and, if the semantics remain narrow and useful, add a policy for
silently unmatched modular instruction rules.

1. Decide whether the policy should be named `--fail-on-ignored-sources` or use
   a more target-specific term; document that it does not reject duplicates or
   shadowed ancestors.
2. Apply the same policy vocabulary to direct inspection and comparison, render
   complete output before exit 1, and preserve invalid-input exit 2.
3. Keep ignored evidence informational without the gate and compose the new
   condition with existing gates using OR semantics.
4. Cover mixed matching, ignored, duplicate, shadowed, and invalid sources over
   multiple targets so the policy cannot broaden accidentally.
5. Run the root portfolio validator plus focused AgentScope checks, update all
   handoffs, and leave a clean descriptive commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency first experience.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not broaden the frontmatter parser or claim undocumented client behavior.
- Keep comparison guidance defined as no applied source across any compared
  profile; do not silently turn it into a profile-parity rule.
- Preserve applied-path divergence and keep invalid/non-applied evidence
  separate.
- Preserve the root CI matrix and temporary-output package smoke tests.

# Next run: retain invalid diagnostics in comparison

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Make profile comparison retain invalid-source evidence instead of reducing each
inspection to applied paths only.

1. Extend comparison results with per-profile invalid counts and ordered source
   diagnostics while keeping common/profile-only applied paths intact.
2. Add an opt-in comparison invalid-source gate that composes with
   `--fail-on-divergence` and renders full human/JSON output before exit 1.
3. Decide and document the comparison schema bump; keep inspection schema v5
   stable unless its existing contract actually changes.
4. Cover consistent-invalid, divergent-invalid, malformed modular, unreadable
   standard, and invalid-reference cases across human and JSON output.
5. Preserve direct-library compatibility where practical and avoid conflating
   source invalidity with applied-path divergence.
6. Run the root portfolio validator plus focused AgentScope checks, update all
   handoffs, and leave a clean descriptive commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency first experience.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not broaden the frontmatter parser or claim undocumented client behavior.
- Preserve the root CI matrix and temporary-output package smoke tests.

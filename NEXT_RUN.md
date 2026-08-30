# Next run: diagnose unreadable standard instructions

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun feature work.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Make unreadable or non-UTF-8 Copilot standard files diagnosable and enforceable
instead of leaving them in the applied state when content normalization fails.

1. Define a precise read-error contract for standard files without leaking file
   content or unstable platform exception text.
2. Preserve ordered source discovery and recursive-reference behavior where it
   is safe; do not read or expand references from content that cannot be decoded.
3. Count affected files in `invalid_source_count` and make the existing
   `--fail-on-invalid-sources` policy reject them.
4. Cover invalid UTF-8, read failures that can be simulated portably, human/JSON
   output, comparison behavior, and unaffected valid sources.
5. Decide whether the source-state change requires an inspection schema or
   package-version bump; document the compatibility reasoning explicitly.
6. Run the root portfolio validator plus focused AgentScope checks, update all
   handoffs, and leave a clean descriptive commit.

## Guardrails

- Preserve AgentScope's read-only, zero-runtime-dependency first experience.
- Keep ProofRun frozen unless its preserved MVP fails validation.
- Do not broaden the frontmatter parser or claim undocumented client behavior.
- Preserve the root CI matrix and temporary-output package smoke tests.

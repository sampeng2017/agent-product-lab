# Next run: model explicit additional instruction directories

AgentScope is the active product. Continue it rather than restarting discovery
or resuming ProofRun.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and all AgentScope documentation, tests, and implementation. Check Git
status/history and rerun the current AgentScope suite before editing.

## Recommended outcome

Evaluate and, if the contract can stay explicit and safe, add repository-
contained equivalents of Copilot CLI's configured additional instruction
directories.

1. Recheck the current official `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` contract and
   define the exact `AGENTS.md` and `*.instructions.md` discovery behavior.
2. Prefer a repeatable CLI option over implicitly reading the process
   environment; record the effective inputs in human and JSON output.
3. Require every configured directory to exist, be a directory, and remain
   contained by the selected repository after symlink resolution.
4. Define stable ordering relative to repository/session discovery without
   claiming undocumented precedence.
5. Integrate resolved-path, normalized-standard-content, and modular-path
   behavior without hiding provenance.
6. Cover multiple directories, duplicate routes, invalid input, comparison,
   planned targets, and policy exits.
7. Keep user-home `COPILOT_HOME` inputs out of scope unless they can be modeled
   without weakening the repository containment boundary.
8. Update docs/status/log, validate both products, and leave a clean descriptive
   commit.

## Guardrails

- Preserve the read-only, zero-runtime-dependency first experience.
- Keep every modeled client behavior explicit and source-grounded.
- Version JSON when adding the effective directory list.
- Keep inspection informational by default and retain exit 2 for invalid
  repository arguments.
- Keep ProofRun frozen unless its preserved MVP fails validation.

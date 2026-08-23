# `@` reference compatibility

This document records the `@path` import contract modeled by AgentScope's
`copilot-cli` profile as of 2026-08-22.

The primary source is GitHub's current [Copilot CLI custom-instructions
documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions).
It says `.github/copilot-instructions.md`, `AGENTS.md`, and `CLAUDE.md` may
include a file with `@` followed by a relative path; referenced files are read
immediately and may contain nested references. Referenced files must stay in
the repository. Absolute paths and paths beginning with `~/` are not loaded,
and imports are not expanded from `GEMINI.md` or `*.instructions.md`.

GitHub's [Copilot CLI command
reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
also documents cycle, size, and depth guards, but does not publish their exact
limits.

## AgentScope behavior

- A line whose trimmed content begins with `@` is resolved relative to the file
  containing that line.
- A valid referenced file appears immediately after its parent as an `applied`
  source of kind `copilot-reference`. Nested imports follow in depth-first
  order. A file reached more than once is reported once.
- Missing files, non-files, cycles, repository escapes, absolute paths, and
  `~/` paths appear as `invalid` sources. Their reason names the failed rule and
  referring file; they do not increase `applied_count`.
- AgentScope stops before the eleventh import edge. The resulting `invalid`
  source explicitly names AgentScope's 10-edge safety limit. This is a
  conservative product limit, not a claim about Copilot CLI's unpublished
  numeric limit.
- `GEMINI.md` and `*.instructions.md` remain applied when otherwise in scope,
  but their apparent `@` lines are not expanded.
- Symlinks are resolved before containment checks, so a relative path cannot
  use an in-repository symlink to load a file outside the selected root.

Human output renders referenced files and diagnostics in the same ordered
source list as directly discovered instructions. Schema-v1 JSON retains its
existing shape: consumers see the new `copilot-reference` kind and `invalid`
state through the existing `sources` objects. Profile comparison continues to
compare only applied paths, so valid imported content participates in
divergence while invalid edges do not.

## Deliberate boundary

AgentScope does not read or inline file contents into its output, enforce
GitHub's unpublished size guard, expand user-level instructions, or accept
absolute imports. Reference diagnostics are informational in v0.3.0; the
existing missing-guidance and divergence gates keep their prior contracts.

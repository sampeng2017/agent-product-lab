# `@` reference compatibility

This document records the `@path` import contract modeled by AgentScope's
`copilot-cli` profile as of 2026-08-30.

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
- A referenced file that cannot be read or decoded as UTF-8 is an `invalid`
  `copilot-reference`, and recursion stops at that edge. The reason uses a
  stable category plus the referring path without exposing exception details.
- AgentScope stops before the eleventh import edge. The resulting `invalid`
  source explicitly names AgentScope's 10-edge safety limit. This is a
  conservative product limit, not a claim about Copilot CLI's unpublished
  numeric limit.
- `GEMINI.md` and `*.instructions.md` remain applied when otherwise in scope,
  but their apparent `@` lines are not expanded.
- Symlinks are resolved before containment checks, so a relative path cannot
  use an in-repository symlink to load a file outside the selected root.

Human output renders referenced files and diagnostics in the same ordered
source list as directly discovered instructions, with aggregate and per-target
invalid-reference counts. Inspection schema-v5 JSON exposes the same counts as
`invalid_reference_count`, alongside the broader `invalid_source_count`; the
document-level values sum diagnostic occurrences reported for each target. The
existing `sources` object shape is unchanged from schema v1. Profile comparison
schema v4 continues to calculate divergence only from applied paths, so valid
imported content participates while invalid edges do not. Invalid edges are
retained as ordered per-profile diagnostics and contribute to comparison
invalid-source and invalid-reference counts.

Inspection is still informational by default. With
`--fail-on-invalid-references`, any target containing at least one invalid
reference makes the command exit 1. This gate and `--require-instructions` use
OR semantics across all targets: either policy failure returns 1 after the full
report is emitted. The newer `--fail-on-invalid-sources` is broader and also
rejects malformed path instructions, but does not change the reference gate's
contract. Invalid repository arguments retain exit 2.

## Deliberate boundary

AgentScope does not read or inline file contents into its output, enforce
GitHub's unpublished size guard, expand user-level instructions, or accept
absolute imports. Comparison preserves invalid-reference details and its broad
`--fail-on-invalid-sources` gate rejects them, but it does not yet expose the
narrow `--fail-on-invalid-references` policy available during inspection.

# `applyTo` glob compatibility

This matrix records the path matching contract modeled by AgentScope's
`copilot-cli` profile as of 2026-08-21. Patterns and targets are interpreted
relative to the selected repository root and use `/` as the path separator.

The primary source is GitHub's current [Copilot CLI custom-instructions
documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions).
It defines comma-separated patterns and gives explicit examples for `*`, `**`,
root-level files, nested segments, and recursive suffix matching. GitHub's
[repository custom-instructions documentation](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)
publishes the same examples for other Copilot surfaces.

## Executable matrix

| Construct | Representative pattern | Expected behavior |
| --- | --- | --- |
| root wildcard | `*` | matches `root.py`, not `src/root.py` |
| recursive wildcard | `**` or `**/*` | matches files at the root and at any depth |
| root suffix | `*.py` | matches root Python files only |
| recursive suffix | `**/*.py` | matches Python files at the root and at any depth |
| anchored directory | `src/*.py` | matches direct children of root `src/`, not nested children or `other/src/` |
| anchored recursive directory | `src/**/*.py` | matches direct and nested Python files below root `src/` |
| directory at any depth | `**/subdir/**/*.py` | requires a `subdir` segment, then matches direct or nested Python files |
| multiple patterns | `**/*.ts, **/*.tsx` | matches when either trimmed pattern matches |
| one-character wildcard | `src/file?.py` | matches exactly one non-separator character |
| dot paths | `.github/**/*.yml`, `.*` | preserves the leading dot as part of the path |
| explicit relative prefix | `./src/*.py` | treated like `src/*.py` |
| leading slash | `/src/*.py` | not normalized; GitHub documents repository-relative patterns without it |

Every row is represented in `test_apply_to_glob_compatibility_matrix` or the
comma-separated integration test. This keeps documentation and behavior from
drifting independently.

## Compatibility boundary

GitHub's Copilot CLI page does not give an explicit `?` example. AgentScope
retains its already-published, conventional glob behavior: `?` matches one
character other than `/`. Treat that row as a documented AgentScope contract,
not a claim that GitHub guarantees it across every Copilot surface.

AgentScope intentionally does not model character classes, brace expansion,
negation, YAML list matching, or `excludeAgent`. Scalar frontmatter may contain
multiple comma-separated patterns. Unsupported frontmatter forms are explicit
diagnostics defined in the separate [frontmatter compatibility
contract](FRONTMATTER_COMPATIBILITY.md). A leading `./` is accepted as a
harmless explicit relative marker, while a leading `/` is left literal rather
than silently rewritten into a repository-relative match.

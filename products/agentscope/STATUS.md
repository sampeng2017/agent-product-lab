# AgentScope status

## Product shape

AgentScope v0.5.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence; its `copilot-cli` profile combines supported
ancestor formats, evaluates one-line `applyTo` globs, diagnoses malformed path
frontmatter, and recursively resolves supported `@` imports. Human and
versioned JSON output are available, with optional missing-instructions,
invalid-reference, invalid-source, and profile-divergence gates.

## Completed on 2026-08-24

- Replaced the ambiguous path-rule fallback with precise ordered diagnostics
  for missing delimiters or keys, empty scalars, lists, mappings, multiline
  values, duplicate keys, malformed declarations and quotes, and empty comma
  items. Valid nonmatching scalar globs remain `ignored`.
- Added `invalid_source_count` at aggregate and target levels. It covers every
  `invalid` source while preserving `invalid_reference_count` as a narrower,
  backward-compatible subset.
- Added `--fail-on-invalid-sources`, which rejects malformed path instructions
  and invalid references without silently broadening the existing
  `--fail-on-invalid-references` contract.
- Versioned inspection JSON from schema v2 to v3 for the two additive broader
  counts; source objects and comparison schema v1 remain unchanged.
- Added a source-grounded frontmatter compatibility contract, bumped AgentScope
  to 0.5.0, and expanded the suite from 21 to 23 tests.

## Changes since the prior run

AgentScope advanced from treating every unsupported path-instruction form as an
ordinary ignored rule to separating invalid configuration from a valid glob
miss. Repository maintainers can now enforce the distinction in CI while
retaining the narrower reference-only policy when that is all they want.

## Known issues

- The Copilot profile models repository inputs only, not user-level instruction
  directories or configuration.
- Current repository discovery does not yet cover every documented Copilot CLI
  location, including `.claude/CLAUDE.md` and nested standard-location nuances.
- The frontmatter parser deliberately supports only a scalar, comma-separated
  `applyTo`; it diagnoses rather than interprets YAML lists, mappings, and
  multiline values.
- `excludeAgent` is accepted as an uninterpreted sibling key, and character
  classes, brace expansion, and negation are not modeled.
- AgentScope does not reproduce Copilot CLI's unpublished import size guard;
  the local 10-edge depth limit is intentionally product-defined.
- GitHub's Copilot CLI documentation does not explicitly demonstrate `?`;
  AgentScope documents its conventional single-character behavior as a product
  contract rather than claiming universal Copilot compatibility.

## Decisions

- Stay read-only and dependency-free for the first useful experience.
- Use named client profiles rather than a misleading universal scope model.
- Allow nonexistent targets so maintainers can inspect guidance before creating
  a planned file; resolved paths still cannot escape the selected repository.
- Treat malformed path frontmatter as `invalid`, but keep a valid nonmatching
  glob `ignored` so configuration health and target scope stay distinct.
- Keep `--fail-on-invalid-references` narrow; expose the superset explicitly as
  `--fail-on-invalid-sources`, with all inspection gates using OR semantics.
- Count invalid diagnostic occurrences per target because one shared source can
  affect several target assessments; expose reference counts as a subset.
- Version inspection JSON to v3 for additive invalid-source counts while
  keeping source objects and comparison schema v1 stable.
- Continue resolving symlinks before containment checks, expanding references
  only from documented source types, and comparing only applied paths.

## Recommended next step

Audit and implement the remaining repository-scoped Copilot CLI discovery
locations, beginning with `.claude/CLAUDE.md`, with source-linked ordering and
deduplication tests before considering user-level instruction directories.

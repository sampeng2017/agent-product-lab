# AgentScope status

## Product shape

AgentScope v0.6.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile walks repository
standard locations along the target-ancestor chain, evaluates scalar `applyTo`
globs, diagnoses malformed path frontmatter, recursively resolves supported
`@` imports, and deduplicates resolved files across discovery routes. Human and
versioned JSON output are available, with optional missing-instructions,
invalid-reference, invalid-source, and profile-divergence gates.

## Completed on 2026-08-25

- Added source-grounded discovery for nested
  `.github/copilot-instructions.md`, `.claude/CLAUDE.md`, and ancestor modular
  instruction trees.
- Defined a deterministic reporting order: standard locations root-to-target,
  immediate depth-first imports, then root-to-target modular trees sorted by
  path. GitHub's lack of general precedence is documented explicitly.
- Unified direct and referenced source tracking by resolved path, so a file
  reached through an earlier reference is not reported again through a later
  standard or modular route. Equivalent symlink routes follow the same rule.
- Preserved source object shapes, schema-v3 inspection, schema-v1 comparison,
  path-frontmatter and reference diagnostics, and all policy exits.
- Added a discovery compatibility contract, bumped AgentScope to 0.6.0, and
  expanded the suite from 23 to 25 tests.

## Changes since the prior run

AgentScope moved from root-only repository-wide and modular Copilot discovery to
a target-ancestor standard-location model with `.claude/CLAUDE.md`, nested
sources, deterministic presentation, and first-resolved-route deduplication.

## Known issues

- AgentScope has no separate Copilot session-directory input. It therefore
  cannot yet distinguish intermediate session directories from directories
  nested toward the target when modeling modular discovery.
- User-level locations, `COPILOT_HOME`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, and
  interactive source disabling remain out of scope.
- Deduplication recognizes resolved file identity, not identical content stored
  at different paths.
- The frontmatter parser deliberately supports only a scalar, comma-separated
  `applyTo`; it diagnoses rather than interprets YAML lists, mappings, and
  multiline values.
- `excludeAgent` is accepted as an uninterpreted sibling key, and character
  classes, brace expansion, and negation are not modeled.
- AgentScope does not reproduce Copilot CLI's unpublished import size guard;
  the local 10-edge depth limit is intentionally product-defined.
- GitHub's Copilot CLI documentation does not explicitly demonstrate `?`;
  AgentScope documents its conventional single-character behavior as a product
  contract.

## Decisions

- Stay read-only and dependency-free for the first useful experience.
- Use named client profiles rather than a misleading universal scope model.
- Use the selected root and target-ancestor chain as explicit repository
  standard locations until session-directory modeling is added.
- Present direct standard sources root-to-target, expand references immediately,
  and list modular rules afterward in deterministic path order. This is output
  stability, not a precedence claim.
- Deduplicate direct and referenced sources by resolved path; first discovery
  wins.
- Allow nonexistent targets so maintainers can inspect guidance before creating
  a planned file; resolved paths still cannot escape the selected repository.
- Keep inspection schema v3, comparison schema v1, and existing policy behavior
  stable for the additive discovery release.

## Recommended next step

Add an explicit repository-contained session-directory input and distinguish
root, intermediate, session, and target-nested locations so modular instruction
discovery can follow GitHub's documented intermediate-directory exclusion.

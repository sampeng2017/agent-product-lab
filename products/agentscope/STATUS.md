# AgentScope status

## Product shape

AgentScope v0.8.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile uses an explicit
repository-contained session directory to discover standard and modular
instructions, diagnoses malformed path rules and references, and explains both
resolved-path and normalized-content deduplication. Human and versioned JSON
output support missing-instructions, invalid-reference, invalid-source, and
profile-divergence gates.

## Completed on 2026-08-28

- Rechecked GitHub's current duplicate-copy rule and limited content matching to
  repository-wide and agent standard files; modular and imported sources remain
  outside that content map.
- Added conservative whole-file normalization that ignores blank lines, line
  placement, and surrounding line whitespace but never matches partial content.
- Retained the first eligible source as `applied` and reported later distinct
  copies as `duplicate`, naming the first retained path in human and JSON output.
- Continued evaluating relative imports from duplicate wrappers, preventing the
  same copied `@guide.md` line in different directories from hiding distinct
  referenced files.
- Preserved first-resolved-path behavior, session-aware order, path-specific
  diagnostics, policy exits, inspection schema v4, and comparison schema v2.
- Bumped AgentScope to 0.8.0 and expanded the suite from 29 to 31 tests, covering
  all discovery roles, divergent branches, cross-kind copies, partial-content
  distinction, modular exclusions, reference interaction, and both renderers.

## Changes since the prior run

The Copilot model now distinguishes a repeated instruction copy from a separately
applied standard source. Maintainers can see the ignored path and its retained
source instead of receiving an inflated applied count or losing provenance.

## Known issues

- User-level locations, `COPILOT_HOME`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, and
  interactive source disabling remain out of scope.
- Unreadable or non-UTF-8 standard files cannot be content-compared and retain
  the prior applied-source behavior.
- Content normalization deliberately ignores line placement, blank lines, and
  surrounding line whitespace only; it does not attempt Markdown semantics or
  similarity matching.
- A target above the session directory does not reclassify session-intermediate
  directories as target-nested modular locations.
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
- Keep session state explicit, repository-contained, and independent of the
  process working directory.
- Present standard files in stable role order without claiming precedence.
- Deduplicate resolved paths first; among remaining standard files, compare
  normalized complete text across eligible kinds and retain the first route.
- Report later content copies with a distinct `duplicate` state, but continue
  evaluating their relative imports at that source location.
- Exclude modular and imported sources from content-copy matching.
- Keep inspection schema v4 and comparison schema v2 because no object shape
  changed; comparison continues to use applied paths only.

## Recommended next step

Evaluate an explicit, repeatable, repository-contained option for additional
Copilot instruction directories, without implicitly reading
`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` from the environment.

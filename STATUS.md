# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains AgentScope v0.15.0, 43 tests, source-linked
  compatibility contracts, and product documentation.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs. A
  read-only portfolio CI workflow validates both products on Python 3.10-3.14.

AgentScope models two explicit profiles. `agents-md` applies the closest
ancestor `AGENTS.md` and explains shadowed files. `copilot-cli` combines
repository standard locations using explicit repository-contained session and
additional-directory inputs, evaluates scalar `applyTo` globs, expands
supported recursive imports, diagnoses invalid sources, and explains duplicate
instruction content. Inspection and comparison emit human or schema-v5 JSON,
preserve applied, non-applied, and invalid evidence, and can gate missing
guidance, ignored path rules, applied-path divergence, invalid references, or
all invalid guidance.

## Completed today (2026-09-05)

- Added `--fail-on-ignored-sources` to inspection and comparison, exiting 1
  after complete output when any requested target has an `ignored` path rule.
- Kept duplicate copies, shadowed ancestors, malformed sources, missing
  guidance, and profile divergence outside the narrow gate unless their own
  independent policies are also enabled.
- Added composable ignored-count properties without changing schema v5; the
  existing ordered source objects already identify every trigger.
- Added a multi-target regression mixing matched and ignored path rules,
  duplicates, shadows, and invalid sources; the suite grew from 42 to 43 tests.
- Bumped AgentScope to v0.15.0 and kept ProofRun frozen.

## Changes since the prior run

Maintainers can now enforce path-rule coverage in CI without conflating a valid
nonmatch with malformed guidance, deliberate copies, or nearest-file shadowing.
The same flag and exit contract work in inspection and comparison, compose with
all existing gates, and leave the established JSON representation intact.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, nested
  `AGENTS.md` interpretation inside additional directories, and interactive
  file disabling remain out of scope.
- GitHub does not document precedence or nested `AGENTS.md` scope for configured
  directories; AgentScope's direct-file and post-repository order is explicit.
- Multi-target output is target-oriented; it does not yet provide a compact
  source-oriented matrix of which requested targets match each modular rule.
- Content normalization ignores line placement, blank lines, and surrounding
  line whitespace but deliberately avoids semantic similarity.
- The dependency-free frontmatter parser supports only scalar `applyTo` values;
  lists, mappings, multiline values, and `excludeAgent` behavior are not modeled.
- Character classes, brace expansion, glob negation, the client's unpublished
  import size limit, and interactive source disabling are not modeled.
- Client behavior can evolve, so profile assumptions require source-linked tests
  and explicit schema/version changes.
- Root CI currently runs on Ubuntu only; Windows/macOS behavior remains covered
  by portable implementation design and focused platform code, not hosted jobs.

## Decisions

- AgentScope, not ProofRun, is the active product for future runs.
- Keep the first experience read-only, credential-free, and dependency-free.
- Model named agent profiles rather than claiming universal compatibility.
- Treat session and additional-directory inputs as explicit reproducible state;
  never infer them from the process working directory or environment.
- Model only direct `AGENTS.md` and recursive `*.instructions.md` beneath an
  additional directory; avoid undocumented nested-agent scoping.
- Report repository/session locations first and additional directories in caller
  order without claiming client precedence.
- Deduplicate resolved identity first, then normalized content among eligible
  standard/additional agent sources; reject symlink escapes as invalid.
- Require readable UTF-8 before any Copilot source is applied. Use stable read
  categories without exception text and stop reference recursion on failure.
- Preserve planned target support and use schema v5 for inspection and
  comparison; keep applied, non-applied, and invalid evidence distinct.
- Keep comparison divergence based only on applied paths and comparison guidance
  as the union of applied sources across profiles.
- Gate `ignored` path rules separately from duplicate and shadowed sources;
  render complete output before returning policy exit 1.
- Validate all stable supported Python minors in root CI, keep external
  permissions read-only, and build/smoke-install packages outside the checkout.

## Recommended next step

Evaluate a source-oriented coverage view for modular instructions so a
multi-target ignored-rule failure can be diagnosed as a compact rule-to-target
matrix while preserving the current target-oriented schemas.

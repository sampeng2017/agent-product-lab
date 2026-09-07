# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains AgentScope v0.16.0, 45 tests, source-linked
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
all invalid guidance. A separate coverage schema groups modular rules across
requested targets without changing the target-oriented inspection contracts.

## Completed today (2026-09-06)

- Added `agentscope coverage`, a Copilot-specific source-oriented view that
  groups modular instruction outcomes across requested targets.
- Preserved caller target order within each source and first-discovery source
  order, including shared, target-nested, additional-directory, planned-target,
  and malformed-frontmatter behavior.
- Distinguished discovery from matching: each rule reports its discovered
  target count, so targets outside a nested discovery location are absent rather
  than mislabeled ignored.
- Added coverage schema v1, human output, and modular-only ignored/invalid policy
  gates with complete-before-exit rendering.
- Bumped AgentScope to v0.16.0 and expanded the suite from 43 to 45 tests.

## Changes since the prior run

Maintainers can now diagnose an ignored-source failure once per modular rule
instead of scanning repeated target-oriented reports. Existing inspection and
comparison schema v5 output is unchanged; coverage uses an independent schema
v1 and keeps its policy surface deliberately limited to modular rules.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, nested
  `AGENTS.md` interpretation inside additional directories, and interactive
  file disabling remain out of scope.
- GitHub does not document precedence or nested `AGENTS.md` scope for configured
  directories; AgentScope's direct-file and post-repository order is explicit.
- Coverage output is source-oriented but vertically lists occurrences; very
  large source/target sets may benefit from an optional compact table or filter.
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
- Keep modular coverage Copilot-specific, exclude standards/references/copies/
  shadows, and distinguish not-discovered targets from ignored occurrences.
- Version coverage independently at schema v1 rather than changing established
  inspection or comparison schema v5.
- Validate all stable supported Python minors in root CI, keep external
  permissions read-only, and build/smoke-install packages outside the checkout.

## Recommended next step

Evaluate whether large coverage reports need an optional compact table or
source/path filters, using real dogfood before expanding the interface.

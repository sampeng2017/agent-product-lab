# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains AgentScope v0.17.0, 46 tests, source-linked
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
requested targets without changing the target-oriented inspection contracts;
an opt-in compact matrix scales human review while preserving detailed output.

## Completed today (2026-09-07)

- Evaluated the vertical report across mixed source states and up to ten targets,
  finding the repeated occurrence layout hard to scan.
- Added `coverage --compact`, a numbered source-by-target matrix that explicitly
  distinguishes matched, ignored, invalid, and not-discovered outcomes.
- Kept complete source paths/patterns and target paths in ordered legends, with
  the default view retained for per-occurrence reasons.
- Kept coverage schema v1, direct API results, counts, and policy exits stable;
  `--compact` and `--json` are mutually exclusive presentation choices.
- Bumped AgentScope to v0.17.0 and expanded the suite from 45 to 46 tests.

## Changes since the prior run

Maintainers can now see the entire modular source/target relationship at a
glance while retaining the detailed explanation view and unchanged JSON for
automation. Inspection and comparison schema v5 output remains unchanged;
coverage stays on independent schema v1.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, nested
  `AGENTS.md` interpretation inside additional directories, and interactive
  file disabling remain out of scope.
- GitHub does not document precedence or nested `AGENTS.md` scope for configured
  directories; AgentScope's direct-file and post-repository order is explicit.
- Compact coverage still expands horizontally with the requested target count;
  chunking or filters need evidence from real large repositories.
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
- Keep compact coverage presentation-only and preserve ordered full-path legends
  plus the detailed reason-bearing default view.
- Validate all stable supported Python minors in root CI, keep external
  permissions read-only, and build/smoke-install packages outside the checkout.

## Recommended next step

Exercise compact coverage on a real repository with many modular rules and add
chunking or filters only if horizontal growth is demonstrably troublesome.

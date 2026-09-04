# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains AgentScope v0.13.0, 41 tests, source-linked
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
instruction content. Inspection emits human or schema-v5 JSON with policy
gates; comparison emits human or schema-v4 JSON, distinguishes wholly unguided
targets from profile divergence, and can independently gate missing guidance,
applied-path divergence, invalid references, or all invalid guidance.

## Completed today (2026-09-03)

- Defined missing comparison guidance as no applied source under any compared
  profile, so intentional one-profile coverage remains accepted unless the
  separate divergence gate is requested.
- Added `compare --require-instructions` with full-output-before-failure and OR
  composition with divergence, invalid-reference, and invalid-source policies.
- Human comparison output now calls wholly uncovered targets `UNGUIDED` and
  reports an aggregate unguided-target count instead of labeling them
  `CONSISTENT`.
- Preserved inspection schema v5 and comparison schema v4 because existing
  per-profile applied-source lists already encode the new policy condition.
- Covered one-profile coverage, mixed multi-target coverage, empty repositories,
  human output, JSON output, and the comparison exit contract.
- Bumped AgentScope to v0.13.0 and expanded the suite from 40 to 41 tests.
- Warning-strict portfolio validation passed both suites, wheel builds,
  isolated installs, and installed console-command smokes on Python 3.11.

## Changes since the prior run

Profile comparison can now reject wholly uncovered targets without rejecting
intentional profile-specific coverage. Human output distinguishes `UNGUIDED`
from `CONSISTENT` and `DIVERGENT`; JSON consumers retain schema v4 and can derive
the same state from existing applied-source lists. ProofRun stays frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, nested
  `AGENTS.md` interpretation inside additional directories, and interactive
  file disabling remain out of scope.
- GitHub does not document precedence or nested `AGENTS.md` scope for configured
  directories; AgentScope's direct-file and post-repository order is explicit.
- Comparison retains invalid evidence but omits other non-applied states such as
  ignored path rules, duplicate Copilot content, and shadowed `AGENTS.md` files.
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
- Preserve planned target support and use inspection schema v5/comparison v4;
  keep invalid evidence separate from applied-path divergence and provide
  missing-guidance, narrow-reference, and broad-source gates in both modes.
- Define comparison guidance as the union of applied sources across profiles;
  use the separate divergence gate when every profile must cover a target.
- Validate all stable supported Python minors in root CI, keep external
  permissions read-only, and build/smoke-install packages outside the checkout.

## Recommended next step

Retain ignored, duplicate, and shadowed source evidence in comparison output so
profile differences remain explainable beyond applied paths and invalid files.

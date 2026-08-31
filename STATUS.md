# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains AgentScope v0.10.0, 37 tests, source-linked
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
gates; comparison emits human or schema-v3 JSON and can gate divergence.

## Completed today (2026-08-30)

- Made every directly discovered Copilot standard source readable as UTF-8
  before it can be applied, content-compared, or used for reference expansion.
- Added stable, privacy-safe diagnostics that distinguish invalid UTF-8 from
  other read failures without embedding platform exception text.
- Marked unreadable referenced files as invalid `copilot-reference` sources and
  stopped recursion at the failed edge; the narrow reference gate now rejects
  those failures as well as the broader invalid-source gate.
- Preserved discovery order, resolved-path deduplication, valid-source behavior,
  existing source objects, inspection schema v5, and comparison schema v3.
- Added portable tests for invalid bytes, simulated read errors, human and JSON
  output, both policy paths, comparison behavior, and safe expansion stopping.
- Bumped AgentScope to v0.10.0 and expanded its suite from 34 to 37 tests.

## Changes since the prior run

AgentScope no longer treats content it could not inspect as applied evidence.
Read failures now participate in enforceable policy and cannot trigger partial
reference discovery. The prior portfolio CI remains unchanged, ProofRun stays
frozen, and no Sam request is active.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, nested
  `AGENTS.md` interpretation inside additional directories, and interactive
  file disabling remain out of scope.
- GitHub does not document precedence or nested `AGENTS.md` scope for configured
  directories; AgentScope's direct-file and post-repository order is explicit.
- Profile comparison still retains applied paths only; it can reveal an
  unreadable shared `AGENTS.md` as divergence, but does not preserve the invalid
  reason or offer an invalid-source comparison gate.
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
- Preserve planned target support and use inspection schema v5/comparison v3 to
  record the effective additional-directory list.
- Validate all stable supported Python minors in root CI, keep external
  permissions read-only, and build/smoke-install packages outside the checkout.

## Recommended next step

Carry per-profile invalid-source diagnostics into comparison output and add an
opt-in comparison gate without changing applied-path divergence semantics.

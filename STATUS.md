# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains AgentScope v0.14.0, 42 tests, source-linked
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
gates. Comparison emits human or schema-v5 JSON, preserves applied,
non-applied, and invalid evidence per profile, distinguishes wholly unguided
targets from profile divergence, and can gate missing guidance, applied-path
divergence, invalid references, or all invalid guidance.

## Completed today (2026-09-04)

- Added ordered per-profile comparison evidence for `ignored`, `duplicate`, and
  `shadowed` instruction sources while retaining invalid evidence separately.
- Added non-applied counts at profile, target, and comparison-document levels;
  human output now renders state, source kind, path, and explanatory reason.
- Advanced comparison JSON from schema v4 to v5 for the new
  `non_applied_sources` and `non_applied_source_count` fields; inspection stays
  on schema v5 with unchanged source objects.
- Preserved applied-path divergence, missing-guidance classification, invalid
  counts, and every existing policy exit contract.
- Covered matched and unmatched modular rules, content duplicates, nested
  `AGENTS.md` shadowing, multi-target ordering, human output, and JSON output.
- Bumped AgentScope to v0.14.0 and expanded the suite from 41 to 42 tests.

## Changes since the prior run

Profile comparison no longer discards useful evidence merely because a source
did not apply. Maintainers can now distinguish path-rule misses, intentional
content copies, and ancestor shadowing while comparing profiles. These states
remain informational and do not alter divergence or policy behavior. ProofRun
stays frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, nested
  `AGENTS.md` interpretation inside additional directories, and interactive
  file disabling remain out of scope.
- GitHub does not document precedence or nested `AGENTS.md` scope for configured
  directories; AgentScope's direct-file and post-repository order is explicit.
- Comparison reports non-applied evidence but has no policy specifically for an
  ignored modular rule; invalid-only gates deliberately do not reject it.
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
- Keep comparison divergence based only on applied paths. Non-applied evidence
  is explanatory and does not change missing-guidance or invalid-source gates.
- Define comparison guidance as the union of applied sources across profiles;
  use the separate divergence gate when every profile must cover a target.
- Validate all stable supported Python minors in root CI, keep external
  permissions read-only, and build/smoke-install packages outside the checkout.

## Recommended next step

Evaluate a narrow ignored-path policy for inspection and comparison so CI can
reject silently unmatched modular guidance without treating intentional
duplicate or shadowed sources as errors.

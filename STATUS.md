# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains AgentScope v0.11.0, 39 tests, source-linked
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
gates; comparison emits human or schema-v4 JSON and can independently gate
applied-path divergence or invalid guidance.

## Completed today (2026-09-01)

- Retained each profile's ordered invalid sources in direct-library comparison
  results instead of reducing inspections to applied paths alone.
- Added invalid-source and invalid-reference aggregates per profile, target, and
  comparison document in human output and comparison JSON schema v4.
- Added `compare --fail-on-invalid-sources`; it composes with
  `--fail-on-divergence`, renders complete diagnostics, and exits 1 on either
  policy without changing invalid repository input exit 2.
- Kept divergence strictly based on profile-specific applied paths, allowing a
  consistent-but-invalid result to remain accurately labeled.
- Bumped AgentScope to v0.11.0 and expanded the suite from 37 to 39 tests.

## Changes since the prior run

Profile comparison now exposes malformed, unreadable, and invalid-reference
evidence with its profile attribution and discovery order. CI can reject that
evidence independently from source-set divergence. Inspection schema v5 and
existing discovery behavior remain unchanged; ProofRun stays frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, nested
  `AGENTS.md` interpretation inside additional directories, and interactive
  file disabling remain out of scope.
- GitHub does not document precedence or nested `AGENTS.md` scope for configured
  directories; AgentScope's direct-file and post-repository order is explicit.
- Comparison does not yet expose the narrower invalid-reference-only gate that
  inspection provides; its new comparison policy rejects all invalid sources.
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
  keep invalid evidence separate from applied-path divergence.
- Validate all stable supported Python minors in root CI, keep external
  permissions read-only, and build/smoke-install packages outside the checkout.

## Recommended next step

Add a narrow `compare --fail-on-invalid-references` gate for callers that want
to reject broken imports without rejecting other malformed instruction sources.

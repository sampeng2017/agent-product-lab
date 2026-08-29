# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains AgentScope v0.9.0, 34 tests, source-linked
  compatibility contracts, and product documentation.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs.

AgentScope models two explicit profiles. `agents-md` applies the closest
ancestor `AGENTS.md` and explains shadowed files. `copilot-cli` combines
repository standard locations using explicit repository-contained session and
additional-directory inputs, evaluates scalar `applyTo` globs, expands
supported recursive imports, diagnoses invalid sources, and explains duplicate
instruction content. Inspection emits human or schema-v5 JSON with policy
gates; comparison emits human or schema-v3 JSON and can gate divergence.

## Completed today (2026-08-28)

- Rechecked GitHub's current configured-instruction-directory contract and
  limited modeling to the documented `AGENTS.md` and `*.instructions.md` forms.
- Added repeatable `--instructions-dir` to inspection and comparison without
  reading `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` from the environment.
- Enforced existing, repository-contained directories, stable caller ordering,
  and resolved-identity deduplication of equivalent input paths.
- Added direct additional `AGENTS.md` and recursive modular discovery after
  ordinary sources, integrated with imports, globs, content-copy handling,
  planned targets, comparison, and policy exits.
- Reported escaping source symlinks as invalid rather than reading them.
- Recorded effective inputs in human output, inspection schema v5, and
  comparison schema v3; bumped AgentScope to 0.9.0 and grew the suite to 34
  passing tests.
- Revalidated frozen ProofRun without changing its product scope.

## Changes since the prior run

AgentScope can now reproduce configured Copilot directory discovery without
hidden process state. Reports preserve the exact deduplicated input list and
additional sources receive the same explanations and gates as ordinary ones.
ProofRun remains frozen, and no Sam request is active.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, nested
  `AGENTS.md` interpretation inside additional directories, and interactive
  file disabling remain out of scope.
- GitHub does not document precedence or nested `AGENTS.md` scope for configured
  directories; AgentScope's direct-file and post-repository order is explicit.
- Unreadable or non-UTF-8 standard files cannot be content-compared and retain
  applied-source behavior; unreadable modular files are invalid.
- Content normalization ignores line placement, blank lines, and surrounding
  line whitespace but deliberately avoids semantic similarity.
- The dependency-free frontmatter parser supports only scalar `applyTo` values;
  lists, mappings, multiline values, and `excludeAgent` behavior are not modeled.
- Character classes, brace expansion, glob negation, the client's unpublished
  import size limit, and interactive source disabling are not modeled.
- Client behavior can evolve, so profile assumptions require source-linked tests
  and explicit schema/version changes.
- The repository has no root CI workflow; each product is validated separately.

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
- Preserve planned target support and use inspection schema v5/comparison v3 to
  record the effective additional-directory list.

## Recommended next step

Add a root GitHub Actions workflow that validates AgentScope and frozen ProofRun
across supported Python versions, including isolated wheel-install smoke tests.

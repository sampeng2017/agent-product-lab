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
- Root documentation coordinates portfolio decisions and run handoffs. A
  read-only portfolio CI workflow validates both products on Python 3.10-3.14.

AgentScope models two explicit profiles. `agents-md` applies the closest
ancestor `AGENTS.md` and explains shadowed files. `copilot-cli` combines
repository standard locations using explicit repository-contained session and
additional-directory inputs, evaluates scalar `applyTo` globs, expands
supported recursive imports, diagnoses invalid sources, and explains duplicate
instruction content. Inspection emits human or schema-v5 JSON with policy
gates; comparison emits human or schema-v3 JSON and can gate divergence.

## Completed today (2026-08-29)

- Added one root GitHub Actions workflow for pushes, pull requests, and manual
  runs with read-only contents permission and no retained checkout credential.
- Added a Python 3.10-3.14 matrix using the current official checkout and Python
  setup action majors; the oldest supported runtime treats warnings as errors.
- Added one reusable local validator that runs both unit suites, compiles both
  packages, builds wheels without publishing, installs them into isolated
  environments, and exercises both console commands.
- Made CI install the shared declared `setuptools>=68` build requirement and
  added a concise local preflight when the selected interpreter lacks it.
- Kept all generated artifacts, bytecode, and virtual environments in a
  temporary directory that is removed at exit, leaving the checkout unchanged.
- Documented exact local use, build-backend preflight, platform scope, and the
  distinction between active AgentScope and frozen ProofRun validation.
- Revalidated 34 AgentScope tests and 53 ProofRun tests (one expected optional
  pytest-runtime skip) before introducing the workflow.

## Changes since the prior run

The portfolio now has a single maintained validation entry point locally and in
GitHub Actions. Every stable supported Python minor is covered, packaging is
tested from built artifacts rather than editable installs, and warning drift is
caught at the Python 3.10 compatibility boundary. Product behavior did not
change; ProofRun remains frozen, and no Sam request is active.

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
- Preserve planned target support and use inspection schema v5/comparison v3 to
  record the effective additional-directory list.
- Validate all stable supported Python minors in root CI, keep external
  permissions read-only, and build/smoke-install packages outside the checkout.

## Recommended next step

Make unreadable or non-UTF-8 standard Copilot instruction files explicit invalid
sources so existing policy gates cannot accept content AgentScope could not
inspect.

# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains AgentScope v0.19.0, 47 tests, source-linked
  compatibility contracts, and product documentation.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs. A
  read-only portfolio CI workflow validates both products on Python 3.10-3.14.

AgentScope models explicit `agents-md` and `copilot-cli` profiles. Inspection
and comparison emit human or schema-v5 JSON, preserve applied, non-applied, and
invalid evidence, and provide narrow policy gates. Independent schema-v1
coverage groups Copilot modular rules across targets; its human views support
display-only source globs and its compact matrix chunks high-cardinality target
sets without changing underlying evidence.

## Completed today (2026-09-09)

- Revalidated the clean v0.18.0 baseline and found no active Sam message.
- Exercised coverage with 14 modular sources, mixed outcomes, two targets, and
  nested discovery; the unfiltered matrix and legend contained twice the rows
  needed for an API-focused review.
- Added repeatable `coverage --source PATH-GLOB` filtering to detailed and
  compact human output, using the documented repository-relative glob matcher.
- Kept complete totals visible and kept ignored/invalid gates over all sources,
  including filtered-out rules; rejected the option with JSON to preserve the
  complete schema-v1 contract.
- Bumped AgentScope to v0.19.0 and expanded the focused suite to 47 tests.

## Changes since the prior run

Maintainers can now focus a source-dense human coverage report on one subsystem
without hiding repository-wide policy failures. Repeated selectors combine with
OR semantics, retain first-discovery order, and state displayed versus complete
source counts. No inspection, comparison, discovery, public API, or JSON schema
changed.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, nested
  `AGENTS.md` interpretation inside additional directories, and interactive
  file disabling remain out of scope.
- GitHub does not document precedence or nested `AGENTS.md` scope for configured
  directories; AgentScope's direct-file and post-repository order is explicit.
- Coverage has no occurrence-state display filter for focusing directly on
  ignored or invalid rules; source filters currently select paths only.
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
- Keep the first experience read-only, credential-free, dependency-free, and
  explicit about the modeled client profile.
- Keep session and additional-directory state reproducible and contained by the
  selected repository; do not infer it from the process environment.
- Preserve planned targets and keep applied, non-applied, and invalid evidence
  distinct in inspection and comparison schema v5.
- Keep modular coverage Copilot-specific and version it independently at schema
  v1; exclude standards, references, copies, and shadows from this view.
- Treat not-discovered targets separately from ignored glob outcomes.
- Keep compact coverage presentation-only. Chunk after 12 targets using global
  caller-order numbers and retain one complete legend plus the detailed view.
- Keep `--source` human-only and display-only, combine repeated path globs with
  OR semantics, and never narrow aggregate counts or policy evaluation.
- Any future presentation filter must disclose displayed versus complete scope.
- Keep portfolio validation in one root script across Python 3.10-3.14 and
  install wheels only in temporary environments.

## Validation

- Warning-strict Python 3.11 portfolio validation passed 47 AgentScope tests and
  53 ProofRun tests with one expected optional skip.
- Both wheels built, installed in isolated temporary environments, and passed
  console smokes; AgentScope reported version 0.19.0.
- The default Python 3.14 interpreter still lacks the declared local
  `setuptools>=68` build backend, and the validator correctly fails preflight.

## Recommended next step

Evaluate a display-only occurrence-state selector for quickly isolating ignored
or invalid modular rules while retaining complete-result policy gates.

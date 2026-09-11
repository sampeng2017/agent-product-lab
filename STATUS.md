# Product lab status

## Current direction

AgentScope is the active product. It is a local, read-only CLI that explains
which coding-agent repository instructions apply to a target path and why.
ProofRun v1.8.1 remains a preserved completed local MVP.

## Product shape

- `products/agentscope/` contains AgentScope v0.20.0, 48 tests, source-linked
  compatibility contracts, and product documentation.
- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  its complete product history.
- Root documentation coordinates portfolio decisions and run handoffs. A
  read-only portfolio CI workflow validates both products on Python 3.10-3.14.

AgentScope models explicit `agents-md` and `copilot-cli` profiles. Inspection
and comparison emit human or schema-v5 JSON, preserve applied, non-applied, and
invalid evidence, and provide narrow policy gates. Independent schema-v1
coverage groups Copilot modular rules across targets; its detailed and compact
human views support display-only source-path and occurrence-state filtering.

## Completed today (2026-09-10)

- Revalidated the clean v0.19.0 baseline and found no active Sam message.
- Exercised mixed matched, ignored, invalid, and not-discovered modular evidence
  and confirmed state-focused output makes failure diagnosis materially smaller.
- Added repeatable `coverage --state STATE` filtering for all four outcomes in
  detailed and compact human reports.
- Defined source-level mixed-state behavior, AND composition with source globs,
  complete totals and gates, and JSON rejection to preserve schema v1.
- Bumped AgentScope to v0.20.0 and expanded the focused suite to 48 tests.

## Changes since the prior run

Maintainers can now isolate sources involved in ignored, invalid, matched, or
not-discovered outcomes while retaining every occurrence of a selected source.
Repeated states use OR semantics; state and source-path filters use AND
semantics. First-discovery order, full-result gates and totals, public APIs, and
all JSON schemas remain unchanged.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, nested
  `AGENTS.md` interpretation inside additional directories, and interactive
  file disabling remain out of scope.
- GitHub does not document precedence or nested `AGENTS.md` scope for configured
  directories; AgentScope's direct-file and post-repository order is explicit.
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

- AgentScope, not ProofRun, remains active pending a v0.20.0 release audit.
- Keep the first experience read-only, credential-free, dependency-free, and
  explicit about the modeled client profile.
- Preserve inspection/comparison schema v5 and coverage schema v1.
- Keep modular coverage Copilot-specific and treat not-discovered targets
  separately from ignored glob outcomes.
- Keep compact coverage presentation-only and chunk after 12 targets.
- Keep `--source` and `--state` human-only and display-only. Repeated values use
  OR within a selector family, the two families compose with AND, and filtering
  never narrows JSON, aggregate counts, or policy evaluation.
- Avoid adding more filters without demonstrated need; audit release readiness
  and freeze the product if no concrete gap remains.

## Validation

- Warning-strict Python 3.11 portfolio validation passed 48 AgentScope tests and
  53 ProofRun tests with one expected optional skip.
- Both wheels built, installed in isolated temporary environments, and passed
  console smokes; AgentScope reported version 0.20.0.
- Focused tests, source compilation, help inspection, and whitespace checks
  pass. Post-commit ProofRun receipt #68 is valid; the chain has 62 valid sealed
  and 6 legacy unsealed receipts.

## Recommended next step

Perform a release-readiness audit of the v0.20.0 wheel, documentation, help, and
all command surfaces; freeze AgentScope if it reveals no concrete product gap.

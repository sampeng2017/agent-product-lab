# Product lab status

## Current direction

ProofRun v1.8.1 and AgentScope v1.0.0 are frozen local MVPs. The next selected
opportunity is an installed-artifact behavior contract runner for Python CLI
wheels. Its first dogfood case now lives in portfolio validation; the next run
should test whether extracting that case produces a genuinely clearer reusable
tool than bespoke shell.

## Product shape

- `products/proofrun/` contains the frozen ProofRun v1.8.1 implementation and
  product history.
- `products/agentscope/` contains the frozen AgentScope v1.0.0 implementation,
  48 focused tests, compatibility contracts, and a realistic release fixture.
- `products/NEXT_PRODUCT_OPPORTUNITIES.md` records the next-product selection,
  adjacent tools, risk, and smallest useful wedge.
- `scripts/validate-portfolio.sh` runs both suites, builds and isolated-installs
  both wheels, and exercises AgentScope's installed human, JSON, and policy-exit
  surfaces.

## Completed today (2026-09-11)

- Audited AgentScope's implementation, packaging, documentation, help, wheel
  contents, isolated install, and inspection/comparison/coverage surfaces.
- Added a realistic packaged-command fixture and release guard covering all
  three human surfaces plus schema-v5 inspection/comparison and schema-v1
  coverage JSON failure contracts.
- Verified exact policy exit 1 semantics and key aggregate evidence from the
  installed wheel rather than source-checkout imports.
- Promoted AgentScope to v1.0.0 and froze it after finding no remaining concrete
  product defect or release blocker.
- Compared four follow-on opportunities using the observed gap and current
  packaging/tool documentation; selected the narrow artifact behavior runner.

## Changes since the prior run

AgentScope behavior and JSON schemas are unchanged. Portfolio validation now
guards the actual artifact-facing workflows that users rely on, not only package
installation and `--version`. The portfolio has moved from one active and one
frozen product to two frozen MVPs plus a selected, evidence-backed next wedge.

## Known issues

- AgentScope intentionally does not model user-home instruction locations,
  implicit environment loading, interactive disabling, general YAML, or
  undocumented client precedence and import limits.
- AgentScope's hosted portfolio CI remains Ubuntu-only.
- The next-product hypothesis overlaps partly with tox and with short custom CI
  scripts. It should be rejected unless a small declarative contract produces
  materially clearer reuse and diagnostics.
- The repository has no configured Git remote, so local release milestones are
  preserved here but not published.

## Decisions

- Freeze AgentScope at v1.0.0; resume only for a concrete defect or a source-
  backed client compatibility change.
- Preserve AgentScope inspection/comparison schema v5 and coverage schema v1.
- Keep ProofRun frozen at v1.8.1.
- Prototype only installed Python-wheel behavior contracts next; do not expand
  into general environment orchestration, content linting, or metadata checks.
- Treat the existing AgentScope shell audit as the baseline the prototype must
  beat rather than assuming a standalone product is justified.

## Validation

- Warning-strict Python 3.11 portfolio validation passes all 48 AgentScope tests
  and 53 ProofRun tests with one expected optional skip.
- Both wheels build and install in isolated temporary environments; AgentScope
  reports v1.0.0 and ProofRun reports v1.8.1.
- Installed AgentScope inspection, comparison, and coverage human paths pass;
  their JSON policy cases return exit 1 and expose the expected schemas/counts.
- Shell syntax, source compilation, documentation links, and whitespace checks
  pass.

## Recommended next step

Build the smallest standalone artifact behavior contract prototype described in
`NEXT_RUN.md`, dogfood it against AgentScope, and keep it only if it clearly
improves on the current shell function.

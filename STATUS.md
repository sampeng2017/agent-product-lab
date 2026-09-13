# Product lab status

## Current direction

WheelContract v0.1.0 is the active prototype. It checks installed Python CLI
wheel behavior from strict TOML. ProofRun v1.8.1 and AgentScope v1.0.0 remain
frozen local MVPs.

## Product shape

- `products/wheelcontract/` contains the dependency-free implementation, six
  focused tests, user documentation, and product status.
- `wheelcontract.toml` is the first real contract: six installed AgentScope
  human, JSON, and policy-exit cases.
- `scripts/validate-portfolio.sh` tests, builds, and isolated-installs all three
  products, then invokes the installed WheelContract against the already-built
  AgentScope wheel.
- `products/proofrun/` and `products/agentscope/` contain the two frozen MVPs.

## Completed today (2026-09-12)

- Built WheelContract v0.1.0 with project-build and prebuilt-wheel inputs,
  disposable virtual environments, dependency-free installs, and execution
  outside the checkout with Python import-leak variables removed.
- Added strict schema-v1 parsing for ordered cases, explicit installed entry
  points, expected exits, stdout fragments, and top-level scalar JSON fields.
- Added case timeouts, bounded output diagnostics, all-results-before-failure
  reporting, and distinct behavior mismatch (1) versus setup/contract (2) exits.
- Added a Python 3.10 fallback for the documented TOML subset and six focused
  tests using a real minimal wheel.
- Re-expressed the installed AgentScope audit as `wheelcontract.toml`. All six
  cases pass against a built wheel.
- Removed 67 lines of bespoke shell/embedded Python validation and replaced
  them with a reusable installed runner invocation. This demonstrated enough
  clarity and diagnostic reuse to retain the product hypothesis.

## Changes since the prior run

The portfolio has moved from a selected opportunity to a runnable third product.
Frozen-product behavior is unchanged. The release audit added yesterday is now
declarative and exercised by WheelContract itself, while portfolio validation
adds WheelContract's tests, wheel build, isolated install, and console smoke.

## Known issues

- JSON assertions support top-level scalar fields only; there are no nested
  paths, arrays, regexes, or schema validation.
- The runner deliberately has no dependency resolution, environment matrix,
  arbitrary shell, hooks, or configurable working directory.
- Child output is spooled to disposable files before bounded diagnostic reads;
  the limit protects memory/report size, not temporary disk usage.
- Building a local project uses the invoking interpreter with build isolation
  disabled, so its declared build backend must already be present.
- Hosted portfolio CI is Ubuntu-only, and the repository has no Git remote.

## Decisions

- Continue WheelContract beyond the prototype because one 52-line declarative
  contract replaced 67 lines of one-off validator logic and centralizes tested
  failure handling without broadening into tox/nox territory.
- Keep schema v1, explicit argv, shell-free execution, no-dependency install,
  full-result reporting, and one artifact/environment per run as current
  product boundaries.
- Keep ProofRun and AgentScope frozen unless a concrete defect appears.

## Validation

- Warning-strict Python 3.11 portfolio validation passes 6 WheelContract, 48
  AgentScope, and 53 ProofRun tests with one expected optional skip.
- All three wheels build and install in fresh environments; their console
  smokes pass, and installed WheelContract passes all six AgentScope contracts.
- Focused compile, shell/YAML syntax, and whitespace checks pass. Python 3.10
  fallback behavior is unit-covered; no local Python 3.10 interpreter is
  available, while portfolio CI retains its Python 3.10 job.

## Recommended next steps

1. Deliberately break one copied AgentScope fixture expectation and inspect
   installed-runner diagnostics in both local and CI-shaped output.
2. If diagnosis is weak, add a small `--json` runner report containing setup
   identity, ordered case results, assertion failures, exit codes, and bounded
   output previews; otherwise avoid a new output schema.
3. Add a second compact contract against WheelContract's own installed CLI to
   test whether the manifest remains clear outside the motivating product.
4. Reassess product value after that second contract before adding deeper JSON
   selectors or broader environment controls.

No human input is required.

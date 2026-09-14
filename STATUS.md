# Product lab status

## Current direction

WheelContract v0.2.0 is the active prototype. It checks installed Python CLI
wheel behavior from strict TOML, now across AgentScope and its own installed
CLI. ProofRun v1.8.1 and AgentScope v1.0.0 remain frozen local MVPs.

## Product shape

- `products/wheelcontract/` contains the dependency-free implementation, six
  focused tests, a compact installed self-contract, documentation, and status.
- Root `wheelcontract.toml` remains the six-case installed AgentScope contract.
- `scripts/validate-portfolio.sh` tests, builds, and isolated-installs all three
  products, then runs installed WheelContract against its own and AgentScope's
  already-built wheels.
- `products/proofrun/` and `products/agentscope/` contain the two frozen MVPs.

## Completed today (2026-09-13)

- Deliberately ran one missing-text, one wrong-exit, and one wrong-JSON-field
  failure against installed AgentScope while retaining a passing control.
  Existing diagnostics were complete, so no structured report was added.
- Added strict `stderr_contains` assertions after WheelContract's stable CLI
  errors exposed the motivating contract's stdout-only assumption.
- Added a three-case self-contract covering installed version, missing-contract
  stderr, and help behavior. Portfolio validation now runs it against the built
  WheelContract wheel before validating AgentScope.
- Strengthened the aggregate-failure regression to pin exact diagnostic details
  for text, exit, and JSON mismatches. Promoted the prototype to v0.2.0 while
  keeping schema version 1 and all existing execution boundaries.

## Changes since the prior run

WheelContract now proves that its manifest generalizes beyond the motivating
AgentScope contract. Frozen-product behavior is unchanged. The only runner
surface addition is symmetric stderr substring checking; human output, exit
semantics, isolation, and schema version remain stable.

## Known issues

- JSON assertions support top-level scalar fields only; there are no nested
  paths, arrays, regexes, or schema validation.
- The runner deliberately has no dependency resolution, environment matrix,
  arbitrary shell, hooks, or configurable working directory.
- Child output is spooled to disposable files before bounded diagnostic reads;
  the limit protects memory/report size, not temporary disk usage.
- Building a local project uses the invoking interpreter with build isolation
  disabled, so its declared build backend must already be present.
- Timeout handling is not yet proven against commands that spawn descendants;
  process-tree cleanup is the next safety audit.
- Hosted portfolio CI is Ubuntu-only, and the repository has no Git remote.

## Decisions

- Continue WheelContract because both a six-case AgentScope contract and a
  three-case self-contract remain clearer than focused install/assertion shell,
  and the second artifact produced one narrow reusable feature rather than
  pressure toward a general task runner.
- Do not add structured runner output: the deliberate three-failure probe was
  fully diagnosable from the existing bounded human report.
- Keep schema v1, explicit argv, shell-free execution, no-dependency install,
  full-result reporting, and one artifact/environment per run as boundaries.
- Keep ProofRun and AgentScope frozen unless a concrete defect appears.

## Validation

- Warning-strict Python 3.11 portfolio validation passes all 6 WheelContract, 48
  AgentScope, and 53 ProofRun tests with one expected optional skip.
- All three wheels build and install in fresh environments; console smokes, the
  three-case WheelContract self-contract, and six-case AgentScope contract pass.
- Compilation, shell syntax, and whitespace checks pass.
- Python 3.10 fallback behavior is unit-covered; no local Python 3.10 interpreter
  is available, while portfolio CI retains its Python 3.10 job.

## Recommended next steps

1. Build a disposable child-spawning CLI fixture and deliberately time it out.
2. Verify whether descendants survive or interfere with temporary cleanup on
   Unix and Windows; add bounded process-tree cleanup only if demonstrated.
3. Keep the existing schema, synchronous ordered execution, and complete result
   reporting unless the lifecycle test requires a narrowly scoped change.
4. Reassess release readiness after the timeout audit; avoid selectors, nested
   JSON, or environment controls without a real third-product contract.

No human input is required.

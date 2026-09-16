# Product lab status

## Current direction

WheelContract v1.0.0 is now the portfolio's third frozen local MVP, alongside
ProofRun v1.8.1 and AgentScope v1.0.0. The next selected experiment is a narrow
release-fact consistency checker, prompted by real version drift found during
today's release audit.

## Product shape

- `products/wheelcontract/` contains the frozen dependency-free implementation,
  10 focused tests, a compact installed self-contract, and release documentation.
- Root `wheelcontract.toml` remains the six-case installed AgentScope contract.
- `scripts/validate-portfolio.sh` tests, builds, and isolated-installs all three
  products, then runs both WheelContract behavior contracts.
- `products/proofrun/` and `products/agentscope/` contain the earlier frozen MVPs.

## Completed today (2026-09-15)

- Ran a warning-strict clean baseline and audited WheelContract's implementation,
  tests, package metadata, wheel contents, help/version, source and installed
  invocation, manifests, setup/behavior exits, output limits, and timeout path.
- Demonstrated and fixed two release blockers: `--wheel` silently accepted a
  project directory, and the Python 3.10 fallback accepted duplicate TOML keys
  that the standard parser rejects.
- Added two regression methods, bringing WheelContract from 8 to 10 focused
  tests. Preserved schema v1, synchronous lifecycle ownership, and exits 0/1/2.
- Corrected the stale v0.1.0 claim in `products/README.md`, promoted
  WheelContract to v1.0.0, and froze it as the third local MVP.
- Compared four next-product opportunities from current repository evidence and
  selected a bounded release-fact consistency experiment.

## Changes since the prior run

Wheel overrides now mean exactly one existing `.whl`, and Python 3.10 parsing
shares the standard parser's duplicate-key/section rejection. No manifest field,
assertion, report, or success/failure semantic changed. Frozen ProofRun and
AgentScope behavior remains unchanged.

## Known issues

- WheelContract intentionally supports only top-level scalar JSON assertions and
  no dependency resolution, environment matrix, shell, hooks, or custom cwd.
- Child output is spooled before bounded reads; the bound protects memory and
  reports rather than temporary disk usage.
- Successful daemonization remains outside the synchronous contract model.
- Timeout cleanup is live-tested on macOS; Windows is unit-covered but not live.
- Hosted portfolio CI is Ubuntu-only, and the repository has no Git remote.

## Decisions

- Freeze WheelContract at v1.0.0 with schema v1 and exits 0/1/2 stable.
- Keep all three completed products frozen unless validation exposes a concrete
  regression.
- Prototype a read-only release-fact consistency checker next, but retain it
  only if its declaration and diagnostics beat a focused `rg`/shell check.

## Validation

- The pre-change warning-strict Python 3.11 portfolio baseline passed 8
  WheelContract, 48 AgentScope, and 53 ProofRun tests with one expected skip.
- Focused post-fix validation passes all 10 WheelContract tests and compilation.
- The audit wheel contains only intended package and metadata files; name,
  version, Python requirement, license, summary, entry point, help, and version
  are correct.
- A post-commit ProofRun pass adds a valid sealed receipt and confirms the named
  `unit` evidence applies to the committed repository state.

## Recommended next steps

1. Prototype the release-fact experiment in `products/releasefact/` against a
   fixture modeled on today's stale version claim.
2. Compare its config and complete mismatch report with the equivalent focused
   shell; abandon it if the product adds ceremony without clearer evidence.
3. Keep the first slice read-only and local: one canonical TOML value, explicit
   file claims, deterministic diagnostics, and no auto-rewrite behavior.

No human input is required.

# Product lab status

## Current direction

WheelContract v0.3.0 is the active prototype. It checks installed Python CLI
wheel behavior from strict TOML, now across AgentScope and its own installed
CLI. ProofRun v1.8.1 and AgentScope v1.0.0 remain frozen local MVPs.

## Product shape

- `products/wheelcontract/` contains the dependency-free implementation, eight
  focused tests, a compact installed self-contract, documentation, and status.
- Root `wheelcontract.toml` remains the six-case installed AgentScope contract.
- `scripts/validate-portfolio.sh` tests, builds, and isolated-installs all three
  products, then runs installed WheelContract against its own and AgentScope's
  already-built wheels.
- `products/proofrun/` and `products/agentscope/` contain the two frozen MVPs.

## Completed today (2026-09-14)

- Reproduced the timeout lifecycle defect with a real disposable wheel: killing
  only its direct installed command left a child alive long enough to write a
  marker after the contract returned.
- Replaced direct-child timeout handling with isolated case process groups and
  bounded tree cleanup. Unix receives graceful group termination, a fixed
  half-second grace, and a forced residual kill; Windows uses native `/T /F`
  tree termination with a bounded invocation and direct-process fallback.
- Added an end-to-end child that ignores graceful termination plus a focused
  Windows invocation contract. Promoted WheelContract to v0.3.0 without changing
  schema v1, manifest options, diagnostics, or exit semantics.

## Changes since the prior run

Timed-out installed commands can no longer leave reproduced descendants behind
on Unix. Frozen-product behavior and both checked-in contracts are unchanged;
the fix alters process ownership only, with no new manifest or CLI surface.

## Known issues

- JSON assertions support top-level scalar fields only; there are no nested
  paths, arrays, regexes, or schema validation.
- The runner deliberately has no dependency resolution, environment matrix,
  arbitrary shell, hooks, or configurable working directory.
- Child output is spooled to disposable files before bounded diagnostic reads;
  the limit protects memory/report size, not temporary disk usage.
- Building a local project uses the invoking interpreter with build isolation
  disabled, so its declared build backend must already be present.
- Successful commands that intentionally daemonize remain outside the
  synchronous contract model; timeout cleanup is the owned lifecycle boundary.
- Live child-spawning cleanup is verified on macOS and will run in Ubuntu CI
  when hosted; the Windows `/T /F` path is unit-covered but not live-tested.
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
- Treat complete cleanup of a timed-out case tree as a safety invariant; retain
  the fixed grace period rather than adding lifecycle policy to the manifest.
- Keep ProofRun and AgentScope frozen unless a concrete defect appears.

## Validation

- Warning-strict Python 3.11 pre-change portfolio validation passed all 6
  WheelContract, 48 AgentScope, and 53 ProofRun tests with one expected optional
  skip.
- Warning-strict focused validation passes all 8 WheelContract tests, including
  the installed child-spawning timeout and Windows command contract.
- Final warning-strict portfolio validation passes all 8 WheelContract, 48
  AgentScope, and 53 ProofRun tests with one expected optional skip. All three
  wheels build and install, both contracts pass, and compilation is clean.
- Python 3.10 fallback behavior is unit-covered; no local Python 3.10 interpreter
  is available, while portfolio CI retains its Python 3.10 job.

## Recommended next steps

1. Audit WheelContract's wheel contents, metadata, installed help/version,
   timeout diagnostics, both real contracts, and all documentation links.
2. Exercise the timeout regression on Linux through hosted CI when a remote is
   available; do not claim live Windows coverage without a Windows runner.
3. If no concrete product gap remains, promote WheelContract to 1.0.0, freeze
   its behavior/schema, and compare narrow next-product opportunities.
4. Avoid selectors, nested JSON, environment matrices, or lifecycle controls
   without a demonstrated third-product need.

No human input is required.

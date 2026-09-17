# Product lab status

## Current direction

ReleaseFact v0.1.0 is the portfolio's active product experiment.

It is retained after the bounded fixture and real-repository dogfood showed that
an explicit claim allowlist plus complete actual/expected diagnostics is clearer
and more reusable than bespoke `rg`/shell control flow. ProofRun v1.8.1,
AgentScope v1.0.0, and WheelContract v1.0.0 remain frozen local MVPs.

## Product shape

- `products/releasefact/` contains a dependency-free read-only checker, five
  focused tests, a stale three-claim fixture, and a local self-contract.
- Root `releasefact.toml` checks seven real package, product-document, and
  portfolio-document claims against ReleaseFact's canonical project version.
- `scripts/validate-portfolio.sh` now tests, builds, and isolated-installs all
  four products, then runs the installed ReleaseFact and WheelContract checks.
- The first three products remain frozen and behaviorally unchanged.

## Completed today (2026-09-16)

- Ran the warning-strict Python 3.11 baseline: 10 WheelContract, 48 AgentScope,
  and 53 ProofRun tests passed with one expected optional skip; all wheels and
  installed contracts passed.
- Built ReleaseFact v0.1.0 around one canonical dotted TOML string and named
  exact one-line `{version}` claim templates.
- Added deterministic all-claim reporting with actual values and line numbers,
  strict selector cardinality, path containment, schema validation, and exits
  0/1/2 for success, drift, and invalid setup.
- Added five focused tests and a fixture modeled on the WheelContract v0.1.0
  stale portfolio claim. The fixture reports all three independent drifts.
- Compared the contract with focused search/shell, retained the product, and
  dogfooded seven real release claims through the installed wheel.

## Changes since the prior run

The repository now has a fourth product prototype and validates it across the
same source/build/install pipeline as the frozen products. No behavior, schema,
or version changed in ProofRun, AgentScope, or WheelContract.

## Known issues

- ReleaseFact intentionally supports only explicit complete-line templates and
  one canonical TOML string; it does not discover, infer, or rewrite claims.
- Python 3.10 uses a narrow dependency-free reader for the selected canonical
  basic string while 3.11+ uses `tomllib`.
- WheelContract retains its documented output-spooling, daemon, and untested
  live Windows cleanup limits.
- Hosted portfolio CI is Ubuntu-only, and the repository has no Git remote.

## Decisions

- Retain ReleaseFact because the fixture and installed dogfood met the explicit
  clarity and complete-diagnosis threshold.
- Keep schema v1 narrow: no regexes, version semantics, recursive search,
  historical-mention inference, or write mode.
- Keep the first three completed products frozen unless validation exposes a
  concrete regression.

## Validation

- Pre-change warning-strict Python 3.11 portfolio validation passed all frozen
  product tests, builds, installs, and contracts.
- Focused ReleaseFact tests, its passing self-contract, its deliberate
  three-drift fixture, compilation, shell syntax, and diff checks pass.
- Full post-change warning-strict Python 3.11 portfolio validation passes 5
  ReleaseFact, 10 WheelContract, 48 AgentScope, and 53 ProofRun tests with one
  expected optional skip. All four wheels build and isolated-install, the seven-
  claim ReleaseFact dogfood passes, and both WheelContract contracts pass.

## Recommended next steps

1. Exercise a deliberate ReleaseFact bump in a disposable checkout and assess
   whether the seven-claim diagnostics guide the update without noise.
2. Add behavior only if that release rehearsal demonstrates a concrete gap;
   otherwise keep the product narrow and improve documentation or freeze it.
3. Continue to leave the three earlier products frozen.

No human input is required.

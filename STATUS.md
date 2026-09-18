# Product lab status

## Current direction

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

Its disposable release rehearsal and release-readiness audit found no product
gap: the seven-claim report guided a coordinated bump and caught one initially
missed documentation update. ProofRun v1.8.1, AgentScope v1.0.0, WheelContract
v1.0.0, and ReleaseFact v1.0.0 are now frozen.

The next bounded experiment targets a different demonstrated gap: command
validation can create or refresh ignored files while ordinary Git status remains
clean. No fifth product exists yet; `NEXT_RUN.md` defines the decision test.

## Product shape

- `products/releasefact/` contains the dependency-free read-only v1.0.0 checker,
  five focused tests, a stale three-claim fixture, and a local self-contract.
- Root `releasefact.toml` checks seven package, product-document, and portfolio-
  document claims against ReleaseFact's canonical project version.
- `scripts/validate-portfolio.sh` tests, builds, and isolated-installs all four
  products, then runs installed ReleaseFact and WheelContract contracts.
- Wheel builds now consume temporary source copies, keeping PEP 517 `build/` and
  `*.egg-info/` output out of the source checkout.

## Completed today (2026-09-17)

- Ran the warning-strict Python 3.11 baseline: 5 ReleaseFact, 10 WheelContract,
  48 AgentScope, and 53 ProofRun tests passed with one expected optional skip;
  all four wheels and installed contracts passed.
- Rehearsed a 0.1.0 to 0.2.0 canonical bump in a disposable checkout. ReleaseFact
  reported all seven drifts precisely, then caught the one claim omitted from
  the first update attempt before producing a clean pass.
- Audited ReleaseFact wheel contents and metadata, source and installed CLI,
  help/version, contracts, exits 0/1/2, documentation, tests, and the Python 3.10
  fallback. No blocker or behavior gap remained.
- Promoted ReleaseFact to v1.0.0 and froze its schema-v1 read-only surface.
- Fixed the portfolio validator to build from temporary source copies after the
  audit showed direct builds refreshing ignored checkout artifacts despite the
  validator's clean-checkout claim.

## Changes since the prior run

ReleaseFact advanced from an active v0.1.0 prototype to a frozen v1.0.0 local
MVP without behavior or schema changes. Portfolio validation no longer writes
new build metadata into product source directories. The other three frozen
products remain behaviorally unchanged.

## Known issues

- ReleaseFact intentionally supports only explicit complete-line templates and
  one canonical TOML string; it does not discover, infer, or rewrite claims.
- Python 3.10 uses a narrow dependency-free reader for the selected canonical
  basic string while 3.11+ uses `tomllib`.
- Ignored build artifacts from historical validator runs still exist locally;
  they were left untouched because they may predate this run. Future validation
  no longer creates or refreshes them.
- WheelContract retains its documented output-spooling, daemon, and untested
  live Windows cleanup limits.
- Hosted portfolio CI is Ubuntu-only, and the repository has no Git remote.

## Decisions

- Freeze ReleaseFact v1.0.0: the prescribed release rehearsal demonstrated
  complete, useful diagnostics and no need to expand schema v1.
- Preserve ReleaseFact's read-only exits 0/1/2 and narrow matching model.
- Build wheels from temporary source copies so validation fulfills its stated
  checkout-cleanliness contract.
- Explore ignored command residue as a separate bounded opportunity rather than
  reopening ProofRun without evidence that a reusable product is warranted.

## Validation

- Pre-change warning-strict Python 3.11 portfolio validation passed.
- The disposable seven-claim release rehearsal produced exits 1 then 0 as
  expected; installed drift and invalid-setup probes produced exits 1 and 2.
- Release audit verified the intended four modules, license, entry point,
  metadata, help/version, source/installed contracts, and error surfaces.
- Post-change warning-strict Python 3.11 validation passed all 116 tests with
  one expected optional skip, all builds/installs/contracts, shell syntax, both
  ReleaseFact contracts, and diff checks. Full product-tree hashes were
  identical before and after the validator.

## Recommended next steps

1. Run the bounded ignored-residue experiment in `NEXT_RUN.md` against a small
   fixture, including a command that updates an already ignored file.
2. Compare a reusable before/after report with focused `find`/hash shell and
   abandon the product if it adds no clarity.
3. Keep all four completed products frozen unless validation exposes a defect.

No human input is required.

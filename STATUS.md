# Product lab status

## Current direction

On 2026-10-05 the root CI baseline was made explicit with `ubuntu-24.04`,
retaining the OS observed in the latest green job. `docs/CI_PLATFORM.md` records
the rationale, limits, review deadline, and upgrade procedure.

The six completed local MVPs remain the maintained portfolio and GrammarCheck
remains archived. The public matrix is green and GitHub detects MIT. External
users have tested installation paths and runnable workflow examples. The new
WheelContract replay exposes a concrete release gap: source tests pass while
the built wheel omits its advertised console command. A metadata correction
makes the same artifact-behavior contract pass.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- ProofRun, AgentScope, WheelContract, ReleaseFact, ResidueCheck, and WheelFact
  remain frozen and covered by portfolio validation.
- `products/grammarcheck/` remains runnable decision evidence with four tests,
  but is excluded from active validation and the release portfolio.
- WheelFact v1.0.3 keeps schema v1 and the exact-contract CLI unchanged. Its
  `verify_wheel_integrity` library hook reuses the same safe archive inventory,
  complete `RECORD` membership, secure hash, and declared-size validation.
- Portfolio validation derives `SOURCE_DATE_EPOCH` from the latest Git commit,
  performs two isolated wheel builds per product, rejects byte drift, checks
  all six first artifacts for integrity, and then installs and exercises them.
- Installed ReleaseFact checks its existing seven portfolio claims plus one
  local three-claim runtime/README/STATUS contract for every maintained product.
- `docs/INSTALLATION.md` documents six separate packages and their console
  commands, virtual environments, a tested public source revision, checkout
  installs, updates, and troubleshooting.
- `examples/proofrun-stale-proof/` contains a minimal unittest project, a
  disposable replay script, and a guide to the actual command results.
- `examples/agentscope-rule-scope/` contains a two-target fixture and replay
  that correct a misdirected modular rule using installed AgentScope v1.0.0.
- `examples/wheelcontract-entry-point/` contains a real setuptools CLI project,
  passing source tests, a two-case release contract, and a disposable replay.

## Completed today (2026-10-05)

- Inspected synchronized `b0b174b`, public MIT metadata, the green matrix, and
  its setup log: Ubuntu 24.04.5 and image `ubuntu-24.04`.
- Verified GitHub's October 19–November 19 alias migration and supported label.
- Preserved that baseline, documented review by November 5 or an earlier
  platform/deprecation event, and left product runtime interfaces unchanged.
- Local warning-strict validation passed 133 tests with one expected skip,
  twelve reproducible builds, six installs, and all existing contracts.

## Prior run (2026-10-04)

- Confirmed MIT detection, synchronized `da1b04a`, no public issues/PRs, and
  green hosted CI at the starting commit.
- Compared artifact-release onboarding, runner pinning, and contract-independent
  integrity CLI expansion. Selected the demonstrated first-user packaging gap
  while retaining current runtime interfaces.
- Built a sample wheel with passing source greeting/version tests but no
  `[project.scripts]`. Both installed-command cases fail with precise missing
  command diagnostics and exit 1, even though build/install succeed.
- Added the standard console entry point only in a temporary copy; rebuilding
  and isolated installation make the unchanged contract pass both cases.
- Installed pinned WheelContract in a fresh environment, supplied the declared
  backend explicitly, and replayed from both the lab and another directory.
- Documented build-environment prerequisites, setup-versus-behavior exit codes,
  source import isolation, correction, and adaptation to a reader's own wheel.

## Changes since the prior run

The root workflow now selects its OS series instead of following a moving alias.
No interpreter matrix, product command, schema, or package version changed.

The prior run clarified instruction scope. This run gives CLI maintainers a
complete installed-artifact release rehearsal instead of a contract that
requires them to invent a package and all setup steps. Runtime implementations,
versions, schemas, command-line interfaces, and installation pins are unchanged.

## External-user value

Published release results keep their known OS baseline through GitHub's alias
migration. Users can see its limits and the criteria for an intentional upgrade.

Readers can reproduce a release defect invisible to direct function tests,
interpret the missing installed command, correct its packaging declaration,
and reuse a small contract for their own CLI. Explicit backend setup removes
a separate first-run failure caused by WheelContract's disabled build isolation.
Wheels, build metadata, caches, and corrections remain in a disposable copy.

## Known issues

- Hosted portfolio CI remains Ubuntu-only.
- There is no published tag or release. The guide pins the tested public
  `84e76fa` revision; maintainers must deliberately refresh it for future runtime
  changes. Source pinning does not pin build dependency versions.
- Windows activation is documented from Python's official instructions but was
  not executed on this macOS host; installed workflow rehearsal used Python 3.11.
- The demos were executed on macOS with installed tools under Python 3.11;
  their scripts support Python 3.10 syntax, but Windows replay is not tested.
- Hosted images and dependencies still update despite the explicit OS label.
  Review the platform choice by November 5. Windows and Ubuntu 26.04 are not
  validated release baselines.
- The archived GrammarCheck code uses CPython's documented best-effort target
  grammar and is not exact interpreter compatibility evidence.
- Standard setuptools sdists were not byte-reproducible across source copies in
  the prior rehearsal because tar member mtimes retained wall-clock state; the
  portfolio does not publish sdists.
- Local validation requires an interpreter with `setuptools>=77`; the default
  `python3` on this host fails that preflight, while `python3.11` passes.
- Internal `RECORD` consistency is not provenance, authenticity, or signature
  verification. WheelFact deliberately makes no such claim.
- Product-local ReleaseFact contracts intentionally cover only canonical
  runtime and frozen handoff claims; historical version examples are not
  release assertions.
- The new release fixture is intentionally incomplete before replay. Its
  sample builds require `setuptools>=77` in the invoking environment and have
  no runtime dependencies; WheelContract does not resolve application dependencies.

## Decisions

- Retain the example only after real builds reproduce source success, missing
  installed behavior, and corrected behavior under the same contract.
- Use an explicit build-backend prerequisite rather than installing dependencies
  from the replay script. Installation instructions already pin the tool source.
- Keep `PYTHONPATH` only in the fixture source-test subprocess; run WheelContract
  through its installed package with checkout import variables removed.
- Do not expand the integrity CLI or create another mandatory release gate.
  Keep the approaching runner-platform decision separate from this user workflow.

## Validation

- Pre-change warning-strict Python 3.11 portfolio validation passed all 133
  maintained tests with one expected skip, twelve reproducible builds, six
  installs, seven ReleaseFact contracts, all behavior contracts, and six wheel
  integrity checks.
- Public run 37173398504 passes on Python 3.10, 3.11, 3.12, 3.13, and 3.14 at
  the inspected starting commit.
- The installed release replay passed repeatedly and from outside the lab.
  Its two source tests pass, the broken artifact's two cases fail with exit 1,
  and the corrected artifact's same cases pass with exit 0.
- Missing backend and missing installed WheelContract each produce documented
  exit 2. Example Python 3.10 grammar/compilation and 39 local links/anchors pass.
- Final warning-strict portfolio validation passed 133 tests with one expected
  skip, twelve reproducible builds, six installs, seven ReleaseFact contracts,
  all behavior contracts, and six integrity checks. ReleaseFact, shell syntax,
  license identity, and diff checks passed. The normal push must match local
  HEAD and its hosted matrix result must be inspected.

## Recommended next steps

1. Review the explicit platform policy by November 5 or an earlier relevant
   event; test Ubuntu 26.04 in a deliberate trial before changing the baseline.
2. Reassess installation and first-use workflows for further concrete friction;
   avoid another worked example without a newly demonstrated interpretation gap.
3. Keep the six product schemas and command-line contracts frozen absent a
   demonstrated correctness or safety defect.

No human input is required.

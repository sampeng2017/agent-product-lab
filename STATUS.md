# Product lab status

## Current direction

Carry WheelContract's tested local release check into an adopter's GitHub CI.
The new copyable starter builds one wheel and checks that exact artifact before
any publication. Runtime versions, contract schemas, and public install pins
remain unchanged; WheelContract is still v1.0.4.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six maintained tools retain source/build/install/contract validation.
- GrammarCheck remains archived; no new product or active portfolio gate was added.
- Public entry points include installation, three worked examples, and now a CI guide.
- Root CI remains Ubuntu 24.04 / Python 3.10–3.14; review policy by November 5.

## Completed today (2026-10-10, 19:59 PDT run)

- Started clean at synchronized bd76c8d. Inspected memory, Git/history, root and
  product docs, source/tests, active To-Sam, workflow/validator, and public GitHub.
  MIT detection and baseline matrix 38019846678 were healthy; no active Sam note.
- Warning-strict baseline passed 138 tests with one expected optional skip and
  existing build/install/contracts/integrity checks.
- Selected a concrete adoption handoff over speculative decoder rules or a
  broader Windows validation change. Existing instructions stopped at local
  invocation; the lab workflow was portfolio-specific.
- Added docs/WHEEL_RELEASE_CI.md and docs/templates/wheelcontract-ci.yml for
  setuptools CLIs without runtime dependencies. The template is not active here.
- The exact YAML build/check block failed the existing broken wheel with two
  missing-command cases, then passed after only adding its entry point. The
  contract's SHA-256 stayed unchanged.
- Rehearsed with a fresh pinned public checker, paths containing spaces, source
  import variables present, and an invalid stale wheel in dist/. Temporary output
  was cleaned and the stale artifact was not selected.
- Verified both official action commits against v7 refs and the successful CI
  job log. The starter uses read-only permissions and retains no checkout credentials.
- Linked the guide from root/product/install/replay surfaces; kept product
  implementation, versions, source pins, and active lab workflow unchanged.

## Changes since the prior run

The prior run repaired case-launch failures and refreshed the runtime install
pin. This run turns that accepted checker into a copyable CI configuration,
without reopening runtime behavior or adding another mandatory internal gate.

## External-user value

Maintainers can add an artifact behavior check to their own pull requests
without extracting the portfolio validator. Source tests cannot hide a missing
installed command, and the check receives the exact wheel the build produced.
The guide explains failure interpretation and what must change for a real project.

## Known issues

- The starter is setuptools / Python 3.11 / Ubuntu 24.04 scoped. It does not model
  packages requiring third-party runtime dependencies; outer-job dependencies
  are not inherited by WheelContract's isolated environment.
- Its build/check shell was locally rehearsed. Root portfolio CI is not evidence
  that the external-project template was hosted; no such claim is made.
- Branch protections, publishing dependencies, and release jobs require the
  adopting maintainer's separate configuration. This starter publishes nothing.
- Action and checker sources are pinned; build dependencies and runner patch
  levels are not. Disposable execution is not a sandbox or authenticity evidence.
- Windows live execution, tagged releases, PyPI distribution, and reproducible
  source distributions remain outside the demonstrated surfaces.

## Decisions

- Retain only if the unchanged YAML shell block and contract diagnose the real
  missing-command gap and pass after a packaging-only correction. That gate passed.
- Prefer standard GitHub workflow structure over a custom action/installer.
- Do not extend the product into dependency or environment orchestration.
- Keep new adoption configuration outside active workflows; do not claim or
  require another internal gate merely because a template exists.

## Validation

- Baseline: 138 tests, one expected optional skip, twelve reproducible builds,
  six installs, release/behavior contracts, and six wheel-integrity checks.
- Fresh VCS installation selected the published WheelContract 1.0.4 code.
- YAML parsing/policy shape and bash syntax passed. Source fixture tests passed.
  Actual shell block returned exit 1 / two failed cases, then exit 0 / two passes.
- Forty-eight local links/anchors, release claims, workflow pin/policy checks,
  and diff checks passed. Warning-strict portfolio revalidation passed the same
  138 tests and all twelve builds / six installs / contracts / integrity checks.
- Zero/multiple output guard rehearsals returned exit 2 before any checker
  invocation and cleaned temporary output; forced-job cleanup is not promised.
- A controlled builder failure retained its exit 73 without invoking the checker.
  Hosted portfolio run 38107471109 passed Python 3.10–3.14 for the published starter.

## Recommended next steps

1. Assess another concrete adopter handoff; do not expand frozen runtime by hypothesis.
2. For a real dependent CLI, use a dependency-aware runner rather than misusing this starter.
3. Follow the November 5 platform-policy review.

No human input is required.

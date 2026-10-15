# Product lab status

## Current direction

Offer a tested, optional pipx installation route for CLI use across repositories.
Keep the project-venv route for development, imports, and Python-driven replays.
All six product runtimes, versions, dependencies, and source pins remain unchanged.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six maintained products; GrammarCheck stays archived.
- Hosted compatibility remains Python 3.10–3.15 on Ubuntu 24.04.
- Installation, existing replays, and the external CI starter remain the public
  entry points. No custom installer or mandatory release gate was added.
- The separate November 5 platform review is unchanged.

## Work today (2026-10-15, resumed 07:51 PDT)

- Started clean at synchronized 81d66fd. Inspected memory, Git/history, root and
  product docs, source/tests, active To-Sam, workflow/validator, and public GitHub.
  MIT and baseline matrix 38587452858 were healthy; no active Sam note existed.
- Local warning-strict baseline passed 140 tests with one expected optional skip,
  twelve reproducible builds, six installs, contracts, and integrity.
- Selected concrete installation friction over another platform trial or
  speculative runtime policy. The guide required activation/manual app paths
  and cautioned against tool environments inside measured trees.
- Used existing pipx 1.7.1 and Python 3.11 with disposable app/home/cache/log/man
  locations. All six published requirements installed; app names, versions,
  subdirectories, and resolved commits matched expectations.
- With no tool environment activated, exposed ProofRun completed preview, init,
  verification, validity, and audit in two separate disposable Git repositories.
- Exposed WheelContract passed its existing three-case prebuilt-wheel contract.
  After injecting pip/setuptools into its own app environment, source build and
  the same contract passed. Project dependencies and target dependencies remain separate.
- Explicit same-source replacement and pip check passed; removing one isolated
  app left the other commands available. No user installation or startup file changed.
- Added the optional route, distribution-versus-command names, lifecycle guidance,
  and replay/import caveats to existing public docs; no new replay fixture added.

## Changes since the prior run

The prior run verified Python 3.15. This run removes per-project tool activation
friction through a standard existing app manager, without reopening frozen code
or altering the supported interpreter/platform matrix.

## External-user value

Users can install a CLI once and use it in multiple repositories, keeping its
environment outside measured project trees. The guide explains which environment
owns project tests and checker build backends, preventing misleading dependency fixes.

## Known issues

- Live app-manager evidence is pipx 1.7.1 / Python 3.11 / macOS. Windows and newer
  backend combinations were not executed here; use upstream installation guidance.
- The pipx app directory must be on PATH. This run did not call ensurepath or
  edit user shell configuration; test commands used a disposable command directory.
- Exposing an app does not make its module importable in another Python. Existing
  Python-driven replay scripts still use the original activated-environment route.
- WheelContract still isolated-installs target wheels without runtime dependencies.
  Injecting a build backend into the checker does not change that target boundary.
- Source revisions select code, not build dependency locks. No PyPI/tag release
  or new authentication/integrity guarantee is advertised.

## Decisions

- Reuse pipx rather than create an installer or silently mutate user PATH.
- Keep the original environment route and all current source pins.
- Retain only after exact-source installs and useful multi-repository behavior
  pass without an activated tool environment. That acceptance gate passed.
- Document package names for management and separate tool/project/target environments.

## Validation

- All six pipx app/version/source identities and exposed command smokes passed.
- ProofRun two-repository behavior, WheelContract prebuilt/source contracts,
  explicit replacement, health check, and isolated removal passed.
- Fifty-nine local links/anchors, frozen release claims, and diff checks passed.
- Warning-strict portfolio revalidation passed 140 tests (one expected skip),
  twelve reproducible builds, six installs, contracts, and wheel integrity.
- Removing the disposable checker app also left the independent ProofRun
  receipt valid and auditable; repository evidence was not removed with the app.

## Recommended next steps

1. Assess concrete first-use friction before expanding frozen runtime behavior.
2. Keep app-manager assumptions and project/target dependency boundaries explicit.
3. Retain the November 5 platform-policy review.

No human input is required.

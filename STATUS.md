# Product lab status

## Current direction

Let command-only/pipx users run the existing stale-proof replay without installing
ProofRun into the Python that runs the example. New explicit --installed-command
selection preserves the default module route and the full evidence sequence.
All frozen product runtimes, versions, and source pins remain unchanged.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six maintained products; GrammarCheck remains archived.
- Root compatibility remains Python 3.10–3.15 on Ubuntu 24.04.
- The existing ProofRun example gains a launcher option and focused tests;
  no new product, installer, replay fixture, or mandatory release gate is added.
- The November 5 platform review remains separate.

## Work today (2026-10-16, started 08:14 PDT)

- Started clean at synchronized 4f90609. Inspected memory, Git/history,
  root/product docs, implementation/tests, active To-Sam, workflow/validator,
  and public GitHub. MIT and baseline 38757778158 were healthy; no active Sam note.
- Baseline warning-strict portfolio passed 140 tests with one expected optional
  skip and all builds, installs, contracts, and integrity checks.
- Selected a documented first-use gap from the prior pipx work: the existing
  replay always imported ProofRun in the caller's Python, requiring another
  installation even though the user already had its CLI.
- Added explicit command-on-PATH selection, resolved before temporary-directory
  and caller-test-PATH setup. Print the selected command and reuse its absolute
  executable for all ProofRun operations. Default module selection is unchanged.
- Caller Python still runs fixture tests. Missing/unusable commands return setup
  exit 2 with mode-specific hints; missing selection fails before fixture creation.
- Added five focused launcher/setup tests. They pass on local Python 3.11/3.14,
  and replay source parses with Python 3.10 grammar.
- Separate caller/tool environments passed the real full replay, including a tool
  path with spaces; the caller explicitly could not import ProofRun. Default
  module mode also passed. An actual isolated pipx install passed new mode.
- Updated example, install, root/product README, opportunity, and next-run
  guidance. Other Python-driven replays retain their existing environment needs.

## Changes since the prior run

The prior run offered standard pipx installation but documented replay imports
as a limitation. This run removes that limitation for the existing ProofRun
replay through an explicit user choice, without changing product behavior.

## External-user value

Users can see VALID -> STALE -> VALID, exact changed-path JSON, expected failure
exit, and receipt-chain audit with their already-installed app. They do not need
a duplicate module installation or an implicit global-command fallback.

## Known issues

- New live mode evidence is macOS / Python 3.11 / pipx 1.7.1, not Windows.
- The caller still needs Python/Git for the fixture. The tool's app environment
  does not supply project test dependencies.
- The caller chooses its PATH; explicit mode runs that selected installed app.
  Default mode deliberately stays bound to the calling Python.
- Focused replay tests are separate from the existing 140 product tests.
  Root portfolio CI is not a hosted command-only replay claim.
- Other replay scripts remain module/environment bound; source pins and build
  dependency/lifecycle limitations remain as documented.

## Decisions

- Prefer explicit opt-in over silently selecting a different global installation.
- Resolve the command before modifying execution context; keep argv shell-free.
- Retain only if the full unchanged JSON/status/audit sequence passes with a caller
  unable to import ProofRun. That gate passed, as did the original route.
- Preserve disposable fixture behavior and frozen runtime boundaries.

## Validation

- Five focused tests passed warning-strict on Python 3.11 and 3.14; Python 3.10
  syntax checked. Preflight exceptions/timeouts also produce setup exit 2.
- Default, separate-command, and actual pipx replays passed their existing full
  assertions. Checked-in project fixture remained unchanged.
- Full warning-strict portfolio passed 140 product tests (one expected optional
  skip), twelve reproducible builds, six installs, release/behavior contracts,
  and complete wheel integrity. Local documentation links/anchors passed.
- Replay under inherited Git overrides left an unrelated disposable repository's
  HEAD, index, and file unchanged. No real user app locations were modified.

## Recommended next steps

1. Assess concrete caller-versus-app environment friction without broadening runtimes.
2. Keep other replay prerequisites explicit until independently exercised.
3. Retain the November 5 platform-policy review.

No human input is required.

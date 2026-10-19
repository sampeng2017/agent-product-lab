# Product lab status

## Current direction

Help users recover from rejected/stale ProofRun evidence without hiding source
changes or deleting receipts. A tested recovery guide distinguishes failures,
changes during verification, later drift, and safe evidence exports.
All six frozen product runtimes, versions, and source pins remain unchanged.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six maintained products; GrammarCheck remains archived.
- Hosted compatibility remains Python 3.10–3.15 on Ubuntu 24.04.
- Existing installation paths, replays, and the external wheel-CI starter remain.
  No product, replay fixture, installer, or mandatory release gate was added.
- The November 5 platform-policy review remains separate.

## Work today (2026-10-19, started 07:50 PDT)

- Resumed the delayed October 17 heartbeat. Started clean at synchronized
  5208614. Inspected memory, Git/history, root/product docs, source/tests,
  active To-Sam, workflow/validator, and public GitHub. No active Sam note;
  MIT detected and baseline matrix 38924146508 green.
- Warning-strict baseline passed 140 product tests with one expected optional
  skip, reproducible builds, isolated installs, contracts, and wheel integrity.
- Selected a concrete documentation trap over launcher symmetry or speculative
  runtime changes: the product README exported a root report that itself made
  a valid receipt stale. Reproduced this with the published ProofRun source pin.
- Added docs/PROOFRUN_TROUBLESHOOTING.md with read-only triage, reason/action
  mapping, exact mutation JSON fields, generator/test separation, safe exports,
  age/commit explanations, and evidence-preserving integrity guidance.
- Corrected the README export to the default ignored evidence directory and
  linked recovery from root, installation, product, and existing replay docs.
- Exercised seven acceptance groups in disposable copies of the existing
  fixture: missing proof, report-induced drift/recovery, mutation rejection,
  real test failure/repair, history/age/new commit, damaged chain, and pytest
  from a separate project environment. No user files or settings were changed.

## Changes since the prior run

The prior run removed pipx replay friction. This run addresses the next failure
interpretation gap: a successful child command or report export is not the same
as a valid evidence gate. The existing CLI already exposes the needed diagnosis;
the public handoff now explains how to use it.

## External-user value

Users can distinguish a failed test from rejected proof, locate the correct
mutation/drift paths, and save reports without accidentally invalidating proof.
Recovery keeps source and integrity boundaries explicit instead of offering
blanket ignores, receipt deletion, or a misleading report-exit success.

## Known issues

- Live recovery acceptance used macOS / Python 3.11 / pinned ProofRun 1.8.1.
  The separate project environment used pytest 9.1.1; Windows was not exercised.
- Ignore checks assume the default evidence directory after verification.
  Custom stores or already-tracked exports need explicit user review.
- Ignored mutations and transient writes restored before command completion
  remain outside ProofRun's Git boundary. Hash consistency is not authentication.
- Project test dependencies remain separate from an installed/pipx tool.
  Disabling pytest's cache may not fit tests/plugins that depend on it.
- No runtime/schema/version/source-pin change, package-index release, or new
  hosted recovery-example claim is made. Existing build/lifecycle limits remain.

## Decisions

- Fix the actual root-report example and explain existing behavior; do not
  change a frozen product just to suppress a useful rejection.
- Keep diagnostics read-only; verification intentionally runs project commands.
- Preserve original evidence on integrity failure. New verification cannot
  repair earlier chain damage, and no automatic repair is advertised.
- Retain only after installed commands reproduce the problems and safe recovery.
  That acceptance gate passed without adding a mandatory portfolio gate.

## Validation

- Seven installed acceptance groups passed, including exact JSON fields/exits,
  report relocation, repeated ignored exports, and validity/audit after recovery.
- Full warning-strict portfolio baseline and revalidation passed 140 product
  tests (one expected optional skip), twelve reproducible builds, six installs,
  all release/behavior contracts, and complete wheel integrity. An additional
  full warning-strict run passed with project pytest available, exercising the
  optional scaffold test. All 71 local links/anchors passed.
- Existing replay passed both module and explicit-command routes; five focused
  launcher tests passed. The optional real-pytest scaffold test also passed in
  the separate project environment on PATH.

## Recommended next steps

1. Prefer another demonstrated adopter obstacle over more replay/gate symmetry.
2. Preserve tool/project/target dependency and evidence boundaries.
3. Retain the November 5 platform-policy review.

No human input is required.

# Product lab status

## Current direction

Prevent false valid-proof claims when Git state is unavailable. ProofRun 1.8.2
requires recorded and current Git context before accepting evidence, while
preserving command-result history. The first-use feedback path remains; no
outside adoption evidence or outreach authorization is inferred.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six maintained products; GrammarCheck remains archived.
- ProofRun advances to 1.8.2 for a reproduced false-valid correctness defect.
- Other five runtimes, schemas, dependencies, and source pins are unchanged.
- Receipt schema v5, hashes, audit, existing replays, and gates remain unchanged.
- Hosted compatibility is Python 3.10–3.15 / Ubuntu 24.04; November 5 review remains.

## Work today (2026-10-21, started 19:59 PDT)

- Started clean at synchronized 1098b92. Inspected memory, Git/history, root and
  product docs, tests/source, active To-Sam, workflow/validator, and public GitHub.
  MIT detected; baseline 39536878147 green. All-state issues returned no feedback.
- Baseline warning-strict portfolio passed 141 tests (one optional skip),
  twelve reproducible builds, six installs, all contracts and wheel integrity.
- Reproduced init/verify/status outside Git returning VALID and gate exit 0,
  including after an edit. Both snapshots had available=false and no fingerprint.
- Added two failing regressions before the correction. Assessment now reports
  repository state unavailable when recorded or current Git context is absent.
- Keep run/verify command recording, informational status exit 0, consistent
  audit, sealed history, fresh-bound supersession, and unborn repositories.
- Updated package/runtime version, neutral current-release selectors, root/index,
  and recovery/trial guidance. Original August v1.8.1 dates stay historical.
- Consumer pins await exact public-source acceptance before being refreshed.

## Changes since the prior run

The prior run prepared the self-service trial and voluntary feedback form.
This run fixes a concrete internal first-use safety reproduction, not a reported
outside-user problem or a demand result. No new preparation service was added.

## External-user value

A successful command cannot establish current Git-bound proof when snapshots
are unavailable. Users get an explicit stale reason and can retain history,
restore the intended Git context, and record fresh applicable evidence.

## Known issues

- No external feedback/adoption was collected; no outreach or issue posting.
- This changes assessment, not run/verify command execution or command-result
  exits. Use status --require-valid for evidence acceptance.
- Git must be installed. No broad Git-error diagnosis, automatic initialization,
  receipt repair, signing, or filesystem sandboxing was added.
- Ignored/transient mutation and audit-authentication limits remain unchanged.
- Existing platform and voluntary-feedback rendering limitations still apply.
- New consumer revision selection awaits public-source installation.

## Decisions

- Use the frozen-product correctness exception only after a real false gate.
- Fail closed on unavailable evidence without deleting or rewriting history.
- Old unbound receipts stay stale after Git becomes available; fresh bound
  verification can supersede them. Existing bound proof can recover after
  temporary access loss if the original Git state is restored unchanged.
- Do not require a first commit: available unborn repositories remain supported.
- No schema, hash, dependency, telemetry, outreach, or mandatory-gate expansion.

## Validation

- Both regressions failed before the fix. All 55 ProofRun tests passed on
  Python 3.11 and 3.14 (one optional pytest skip per run); Python 3.10 grammar passed.
- Post-fix warning-strict portfolio passed 143 tests (one optional skip), twelve
  reproducible builds, six installs, release/behavior contracts and wheel integrity.
  Exact public-source installation and consumer-pin acceptance follow publication.

## Recommended next steps

1. Complete exact-public-source acceptance and update only ProofRun consumers.
2. Continue reading genuine feedback; obtain authorization before any outreach.
   Do not substitute internal checks for demand evidence.
3. Retain the November 5 platform-policy review.

No human input is required.

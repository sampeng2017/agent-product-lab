# Product lab status

## Current direction

Keep the verified platform stable while awaiting genuine first-use feedback.
The overdue platform review was completed on November 19: retain explicit
Ubuntu 24.04, record fresh hosted evidence, and review again by December 19.
This is routine maintenance, not a new product capability or adoption result.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- Six maintained products; GrammarCheck remains archived.
- ProofRun remains 1.8.2 and WheelContract 1.0.6; other frozen versions unchanged.
- Root CI still uses Python 3.10–3.15 on ubuntu-24.04.
- All runtime sources, source install pins, schemas, workflows, and gates unchanged.
- No Ubuntu 26.04 trial, platform expansion, or release claim was added.

## Work today (2026-11-19, started 19:59 PST)

- Started clean/synchronized at dcf8dd6. Inspected Git/history, memory,
  README/status/log/handoffs, product documentation/tests/source, active To-Sam,
  workflow/validator, and the public GitHub surface.
- MIT detected; all-state issues returned no feedback and no active Sam note.
  The last recorded release CI was green; no outside adoption is inferred.
- Completed the documented November 5 checkpoint late, on November 19.
  Checked official image support/migration information and Python lifecycle.
- Upstream catalog snapshot fbb26cb still lists explicit Ubuntu 24.04 and 26.04;
  its latest-label wording differs from the migration target. Do not infer
  actual alias assignment or a completed cutover from a schedule alone.
- Ran the existing hosted workflow manually on unchanged source dcf8dd6:
  44671600749 passed the complete six-version matrix.
- Setup logs reported Ubuntu 24.04.5 but three image revisions in that one run.
  The policy records exact image/Python versions, not an immutable-image claim.
- Updated the public platform policy, next-run handoff, and dated run log.
  No code, workflow, source pin, product version, or new required check changed.
- Left the first To-Sam request for one voluntary real-work attempt. Sam can
  share the guide himself, decline, or explicitly approve one scoped invitation.
  No participant was contacted and no outreach permission is inferred.

## Changes since the prior run

The previous run fixed ProofRun's unavailable-Git evidence gate. This run
addresses a stale platform-review deadline after a period without recorded
runs, using the existing validation rather than adding features or gates.

## External-user value

Installation and CI users retain a currently verified baseline instead of
receiving an untested OS switch. The public policy distinguishes a planned
alias migration, actual runner metadata, and per-job wheel reproducibility.

## Known issues

- No external feedback, participants, outreach, or demand/retention evidence.
- Ubuntu 26.04 availability is not portfolio compatibility evidence; it was not
  trialed here. Existing Windows/free-threaded/platform limits remain.
- Explicit OS labels still roll software/images; three image revisions appeared
  in one matrix. Source install pins do not lock build dependencies.
- Reproducibility checks compare two builds within each job, not across images.
- Python 3.10 is end-of-life upstream and remains a compatibility floor only.
- The overdue review was not backdated. Next checkpoint is December 19 or an
  earlier platform-release/deprecation trigger.

## Decisions

- Retain supported ubuntu-24.04 after a fresh green matrix and no demonstrated
  need to change OS series. Upgrade only after a separate green proposed-image trial.
- Keep every frozen runtime, interpreter list, source pin, and existing starter.
- Treat healthy maintenance as quiet status, not evidence that the product
  gained users. The new human choice, not routine validation, warrants this
  run's notification. Keep unchanged pending status quiet afterward.

## Validation

- Local warning-strict portfolio passed 143 tests (one expected optional skip),
  twelve reproducible builds, six installs, all release/behavior contracts,
  and complete wheel integrity.
- Fresh hosted run 44671600749 passed Python 3.10–3.15 on the unchanged workflow.
  Actual runner image and Python versions were read from all six job logs.
- All 78 local documentation links/anchors and the active request path passed.
  The seven-claim portfolio release check and diff checks passed.

## Recommended next steps

1. Read genuine first-use feedback and investigate demonstrated blockers;
   seek authorization before outreach. Do not count maintenance as demand.
2. Keep the supported baseline; review by December 19 or an earlier trigger.
3. Trial an OS-series change separately only when there is a reason to adopt it.

No code/CI repair needs input. The next demand experiment needs Sam's choice:
see To-Sam/codex_request_26-11-19.txt (attempt 1/3; no repeat before November 26).

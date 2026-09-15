# Next run: WheelContract release readiness audit

WheelContract v0.3.0 is the active prototype. ProofRun v1.8.1 and AgentScope
v1.0.0 are frozen.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, WheelContract's README and STATUS, implementation, tests, both
contracts, and portfolio validation. Check Git status/history and rerun the
warning-strict portfolio validator before editing.

## Recommended outcome

1. Audit package metadata, wheel contents, installed help/version, source and
   wheel invocation, both checked-in contracts, timeout diagnostics, docs, and
   every CLI option/error surface.
2. Confirm the process-tree regression remains warning-clean and deterministic
   on the available Unix host; distinguish the unit-pinned Windows path from
   live platform evidence.
3. Fix only demonstrated release blockers. Preserve full-result execution,
   strict schema v1, shell-free argv, isolation, output bounds, and exit 0/1/2.
4. If no concrete gap remains, promote WheelContract to 1.0.0 and freeze it as
   the portfolio's third local MVP.
5. Compare narrow next-product opportunities using current evidence, document
   one bounded experiment for the following run, validate all products, and
   commit cleanly.

## Guardrails

- Do not add dependency resolution, environment matrices, hooks, arbitrary
  shell, or general task-runner features.
- Do not add lifecycle configuration or broaden timeout cleanup beyond the
  demonstrated synchronous case boundary.
- Keep both frozen products unchanged unless validation reveals a regression.
- Retain the product only while contracts and diagnostics are materially clearer
  than focused shell for real installed-artifact behavior.

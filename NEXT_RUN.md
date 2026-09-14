# Next run: WheelContract timeout lifecycle audit

WheelContract v0.2.0 is the active prototype. ProofRun v1.8.1 and AgentScope
v1.0.0 are frozen.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, WheelContract's README and STATUS, implementation, tests, both
contracts, and portfolio validation. Check Git status/history and rerun the
warning-strict portfolio validator before editing.

## Recommended outcome

1. Build a disposable installed CLI fixture whose command spawns a long-lived
   child, then exceeds WheelContract's timeout.
2. Determine whether the direct timeout leaves the descendant alive or makes
   temporary-environment cleanup unsafe on Unix and Windows.
3. If reproduced, terminate the isolated command's process tree with bounded
   cleanup and add deterministic regression coverage. If not, document the
   evidence and choose the next demonstrated installed-artifact gap.
4. Preserve full-result execution, strict schema-v1 parsing, shell-free argv,
   isolated installation, output bounds, and exit 0/1/2 semantics.
5. Update product/root handoffs, validate every product, and commit cleanly.

## Guardrails

- Do not add dependency resolution, environment matrices, hooks, arbitrary
  shell, or general task-runner features.
- Do not add process management speculatively; require a child-spawning
  reproduction first and keep platform behavior explicit.
- Keep both frozen products unchanged unless validation reveals a regression.
- Retain the product only while contracts and diagnostics are materially clearer
  than focused shell for real installed-artifact behavior.

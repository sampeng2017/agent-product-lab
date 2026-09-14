# WheelContract status

## Current shape

WheelContract v0.2.0 is a dependency-free prototype for Python CLI maintainers.
It builds or accepts one wheel, installs it without dependencies in a disposable
virtual environment, and checks explicit installed command behavior.

## Implemented

- Strict schema-v1 TOML with one artifact and ordered cases.
- Exact exit, bounded stdout/stderr substring, and top-level scalar JSON
  assertions.
- Isolated execution with checkout import variables removed, no shell, case
  timeouts, complete result reporting, and distinct contract/setup exit 2.
- Python 3.10 fallback parsing for the documented zero-dependency schema.
- A compact installed self-contract covering version, help, and a stable stderr
  diagnostic; portfolio validation runs it before the AgentScope contract.

## Diagnostic finding

A copied AgentScope contract was deliberately broken with one missing human
fragment, one wrong expected exit, and one wrong JSON field. Existing output
named every case and assertion, showed actual and expected values, retained
bounded command output, and completed the passing control. No machine-readable
report was justified. The second artifact did demonstrate a narrower omission:
stable CLI errors live on stderr, so v0.2.0 adds `stderr_contains` without
changing schema version 1.

## Known limits

- Only installed entry points and the environment's `python` can be invoked.
- No dependency installation, build isolation, nested JSON paths, output regex,
  parallel cases, or retained environments.
- Output is bounded for reading and diagnostics, but child output is first
  spooled to disposable files.
- Timeout behavior has not been audited for commands that spawn descendants.

## Next decision

Retain the product after two distinct contracts: both remain expectation-adjacent
and clearer than equivalent environment/install/assertion shell. Next, exercise
timeout behavior with a child-spawning CLI and verify that a disposable run
cannot leave descendant processes behind. Add process-tree cleanup only if that
probe demonstrates the suspected lifecycle gap.

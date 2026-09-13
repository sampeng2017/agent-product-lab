# WheelContract status

## Current shape

WheelContract v0.1.0 is a dependency-free prototype for Python CLI maintainers.
It builds or accepts one wheel, installs it without dependencies in a disposable
virtual environment, and checks explicit installed command behavior.

## Implemented

- Strict schema-v1 TOML with one artifact and ordered cases.
- Exact exit, bounded stdout substring, and top-level scalar JSON assertions.
- Isolated execution with checkout import variables removed, no shell, case
  timeouts, complete result reporting, and distinct contract/setup exit 2.
- Python 3.10 fallback parsing for the documented zero-dependency schema.

## Known limits

- Only installed entry points and the environment's `python` can be invoked.
- No dependency installation, build isolation, nested JSON paths, output regex,
  parallel cases, or retained environments.
- Output is bounded for reading and diagnostics, but child output is first
  spooled to disposable files.

## Next decision

Use the portfolio's AgentScope contract as the continued dogfood case. Prefer
better failure context or a machine-readable runner report only when a real CI
diagnostic gap is observed; reject the product if subsequent contracts become
more verbose or less clear than focused shell.

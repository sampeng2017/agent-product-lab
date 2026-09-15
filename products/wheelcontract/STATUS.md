# WheelContract status

## Current shape

WheelContract v0.3.0 is a dependency-free prototype for Python CLI maintainers.
It builds or accepts one wheel, installs it without dependencies in a disposable
virtual environment, and checks explicit installed command behavior.

## Implemented

- Strict schema-v1 TOML with one artifact and ordered cases.
- Exact exit, bounded stdout/stderr substring, and top-level scalar JSON
  assertions.
- Isolated execution with checkout import variables removed, no shell, case
  timeouts, complete result reporting, and distinct contract/setup exit 2.
- Bounded process-tree cleanup for timed-out cases: graceful then forced process
  group termination on Unix and native `/T /F` tree termination on Windows.
- Python 3.10 fallback parsing for the documented zero-dependency schema.
- A compact installed self-contract covering version, help, and a stable stderr
  diagnostic; portfolio validation runs it before the AgentScope contract.

## Lifecycle finding

The previous direct-child timeout left a spawned installed-wheel descendant
alive long enough to write after the contract returned. The regression uses a
child that ignores graceful termination; v0.3.0 isolates each case and escalates
to a forced group kill before temporary cleanup. The behavior is exercised end
to end on macOS/Unix, and the Windows native tree-termination invocation is
pinned separately because no Windows host is available locally.

## Known limits

- Only installed entry points and the environment's `python` can be invoked.
- No dependency installation, build isolation, nested JSON paths, output regex,
  parallel cases, or retained environments.
- Output is bounded for reading and diagnostics, but child output is first
  spooled to disposable files.
- Successful commands that intentionally daemonize are outside the synchronous
  contract model; only timeout cleanup owns an entire process tree.
- Windows tree cleanup is unit-covered but has not yet had a live Windows
  child-spawning run; hosted portfolio CI is Ubuntu-only.

## Next decision

Retain the product after fixing a demonstrated installed-process safety defect
without expanding the manifest or task-runner scope. Next, perform a release
readiness audit across package metadata, wheel contents, installed help/version,
both real contracts, timeout diagnostics, and documentation. Promote and freeze
the product only if that audit finds no concrete gap.

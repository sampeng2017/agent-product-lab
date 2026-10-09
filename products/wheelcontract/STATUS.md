# WheelContract status

## Product shape

WheelContract v1.0.3 is a frozen, dependency-free local MVP for Python CLI
maintainers. It builds or accepts one wheel, installs it without dependencies in
a disposable virtual environment, and checks explicit installed command
behavior from strict schema-v1 TOML.

## Completed on 2026-10-09

- Reproduced a decoder nesting-limit traceback that aborted the remaining cases
  even though the output stayed inside the configured byte bound.
- Record this as case failure, continue the suite, and retain decoder limits.
- Added real installed-fixture and CLI continuation regressions; promoted 1.0.3.

## Correctness patch on 2026-10-07

- A real installed fixture reproduced five false passing cases with bare
  nonstandard JSON constants, including unasserted nested values.
- JSON assertion cases now reject NaN/Infinity/-Infinity through the decoder;
  quoted strings and ordinary JSON remain compatible. Decode failures report
  behavior exit 1 instead of aborting the suite.
- Added positive/negative and CLI aggregate regressions; promoted to v1.0.2.

## Correctness patch on 2026-10-06

- Reproduced a false passing installed contract: JSON `1`/`0` satisfied boolean
  expectations, and `true`/`false` satisfied numeric expectations through Python
  equality. Added a real installed-wheel regression before fixing the comparison.
- Boolean and numeric categories now remain distinct. Numeric `1`/`1.0` value
  equality and existing string behavior remain compatible.
- All fields still report their mismatches; schema v1 and exits 0/1/2 remain
  unchanged. Promoted the correctness patch to v1.0.1.

## Release audit on 2026-09-15

- Audited package metadata, wheel contents, source and installed invocation,
  help/version, default and explicit manifests, both checked-in contracts,
  failure/setup exits, output bounds, and timeout diagnostics.
- Made `--wheel` reject directories, missing paths, and non-wheel files instead
  of silently treating a project directory as a build source.
- Made the Python 3.10 fallback reject duplicate keys and sections consistently
  with Python 3.11+'s standard TOML parser.
- Added focused regressions for both release blockers and promoted the product
  from v0.3.0 to v1.0.0 without changing schema v1.

## Stable boundary

- One Python project or one existing wheel and one disposable environment per
  contract.
- Ordered, shell-free argument vectors with exact exit, bounded stdout/stderr
  fragments, and top-level scalar JSON assertions.
- Isolated execution with checkout import variables removed, complete result
  reporting, and distinct behavior exit 1 versus contract/setup exit 2.
- Bounded process-tree cleanup for timed-out cases: graceful then forced process
  group termination on Unix and native `/T /F` termination on Windows.

## Known limits

- No dependency installation, build isolation, environment matrix, hooks,
  arbitrary shell, configurable working directory, nested JSON paths, regexes,
  parallel cases, or retained environments.
- Output is bounded for reading and diagnostics, but child output is first
  spooled to disposable files.
- Successful commands that intentionally daemonize are outside the synchronous
  contract model; only timeout cleanup owns an entire process tree.
- Unix child cleanup is live-tested on macOS and will run in hosted Ubuntu CI
  when a remote is available. Windows cleanup is unit-pinned, not live-tested.

## Decisions

- Freeze WheelContract at v1.0.3 and preserve schema v1 plus exit 0/1/2.
- Keep the explicit installed-artifact focus; do not turn it into a general task
  runner or tox/nox replacement.
- Resume work only for a reproducible installed-artifact defect.

## Validation

- The regression failed before the patch and passes afterward. The focused
  suite now contains 13 tests.
- The built wheel contains only package modules, license, entry point, and
  standard distribution metadata; metadata reports version 1.0.3 and Python
  3.10+.
- Portfolio validation builds and isolated-installs all three products, passes
  the WheelContract self-contract and six-case AgentScope contract, and retains
  one expected optional ProofRun skip.

## Recommended next step

Leave WheelContract frozen. Run the bounded release-fact consistency experiment
described at the repository root; reopen only for a concrete regression.

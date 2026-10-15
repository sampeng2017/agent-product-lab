# WheelContract status

## Product shape

WheelContract v1.0.5 is a frozen, dependency-free local MVP for Python CLI
maintainers. It builds or accepts one wheel, installs it without dependencies in
a disposable virtual environment, and checks explicit installed command
behavior from strict schema-v1 TOML.

## CLI installation adoption on 2026-10-15

- Added an optional tested pipx route to the shared guide without changing
  runtime, dependencies, source pins, or the existing project-venv route.
- The exposed 1.0.5 command passed a prebuilt-wheel contract and a source build
  after pip/backend injection into its own app environment.
- Keep target dependency isolation and Python-driven replay prerequisites
  explicit; app availability does not imply imports in another interpreter.

## Interpreter compatibility on 2026-10-14

- The unchanged runtime and build definitions passed the complete hosted
  portfolio on stable CPython 3.15.0 alongside all prior interpreter jobs.
- Retained version 1.0.5, schema, dependencies, source pin, and package minimum.
  Python 3.10 remains a compatibility floor, not an upstream maintenance promise.
- No local 3.15, free-threaded, or additional platform execution is inferred.

## Correctness patch on 2026-10-12

- Reproduced three false JSON passes caused by replacement decoding of malformed
  UTF-8, including an invalid byte matching a literal U+FFFD expectation.
- Validate bounded raw stdout with strict UTF-8 decoding before JSON parsing;
  preserve replacement-decoded previews and non-JSON behavior.
- Added installed-fixture/CLI regressions for invalid sequences, valid Unicode,
  legitimate U+FFFD, continuation, and a byte-limit split of a valid character.
- Promoted 1.0.5 without changing schema v1, exits, or configured bounds.

## CI adoption guide on 2026-10-10

- Added a standalone, non-publishing GitHub Actions starter and setup guide
  outside the lab's active workflow directory. It checks the exact built wheel.
- Rehearsed its unchanged shell block against the existing broken fixture and
  the packaging-only correction with installed v1.0.4; the contract did not change.
- The starter is explicitly setuptools/zero-runtime-dependency scoped. Action
  commits match the successful Ubuntu baseline; external-template execution was
  local, not a new hosted workflow claim. Runtime and installation pin unchanged.

## Correctness patch on 2026-10-09 (evening)

- A real wheel installed a script with an unavailable interpreter. The script
  existed, but starting it raised OSError and aborted all later cases.
- Version 1.0.4 reports launch errors as bounded case failures, records no child
  exit/output for the failed start, and continues the complete suite with exit 1.
- Added a Unix installed-script/CLI regression and a portable permission-error
  diagnostic bound test. Build/install errors remain setup exit 2.

## Correctness patch on 2026-10-09 (morning)

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
- Unix child cleanup is live-tested on macOS and in hosted Ubuntu CI.
  Windows cleanup is unit-pinned, not live-tested.

## Decisions

- Freeze WheelContract at v1.0.5 and preserve schema v1 plus exit 0/1/2.
- Keep the explicit installed-artifact focus; do not turn it into a general task
  runner or tox/nox replacement.
- Resume work only for a reproducible installed-artifact defect.

## Validation

- The regression failed before the patch and passes afterward. The focused
  suite now contains 17 tests.
- The built wheel contains only package modules, license, entry point, and
  standard distribution metadata; metadata reports version 1.0.5 and Python
  3.10+.
- Portfolio validation builds and isolated-installs all six products, passes
  the WheelContract self-contract and six-case AgentScope contract, and retains
  one expected optional ProofRun skip.

## Recommended next step

Leave WheelContract frozen. Assess concrete first-user friction using the root
handoff; reopen only for a reproduced correctness or safety defect.

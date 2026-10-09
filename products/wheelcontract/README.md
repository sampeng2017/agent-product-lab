# WheelContract

WheelContract verifies the behavior users receive from an installed Python CLI
wheel. It builds a local project or accepts an existing `.whl`, installs that
single artifact without dependencies in a disposable virtual environment, and
runs explicit argument vectors from a small TOML contract.

The v1.0 local MVP focuses on the release gap demonstrated by this portfolio:
source tests can pass while an installed command, JSON shape, or documented
policy exit has regressed.

## Install

Use the [tested Git installation guide](../../docs/INSTALLATION.md#wheelcontract-103)
to install this package alone. Then create a contract like the one below and run
`wheelcontract --wheel dist/example.whl wheelcontract.toml` with your wheel path.

[Replay the missing-command release example](../../examples/wheelcontract-entry-point/README.md)
to see passing source tests, a wheel without its console entry point, and a
metadata correction that makes the same installed-behavior contract pass.

## Contract

```toml
schema_version = 1

[artifact]
# Local project directory or one .whl, relative to this file.
source = "."

[run]
timeout_seconds = 30
max_output_bytes = 65536

[[case]]
name = "version"
argv = ["example", "--version"]
stdout_contains = ["example 1.0"]

[[case]]
name = "usage-error"
argv = ["example", "--unknown-option"]
exit = 2
stderr_contains = ["unrecognized arguments: --unknown-option"]

[[case]]
name = "policy-json"
argv = ["example", "check", "--json", "--strict"]
exit = 1

[case.json]
schema_version = 2
failure_count = 1
```

Each command must name an installed console entry point or `python`; shell
evaluation and command paths are rejected. Arguments may include
`{manifest_dir}` to refer to checked-in fixtures without relying on the caller's
working directory. Every case runs from a clean temporary directory with common
Python import-leak variables removed. Cases default to exit 0, and repeated
`stdout_contains` and `stderr_contains` fragments plus top-level scalar JSON
fields are supported.

Each case runs in a distinct process group. On timeout, WheelContract terminates
the full group, waits for a short fixed grace period, then force-kills residual
descendants before removing the disposable environment. Unix uses session and
process-group signals; Windows uses native process-tree termination.

The runner executes every case and reports every failure. Exit 0 means all
contracts passed, 1 means behavior differed, and 2 means the manifest, build, or
installation was invalid. Output beyond `max_output_bytes` fails the case and is
truncated in diagnostics; each case also has a timeout.

## Run locally

```bash
PYTHONPATH=src python3 -m wheelcontract path/to/wheelcontract.toml
PYTHONPATH=src python3 -m wheelcontract --wheel dist/example.whl wheelcontract.toml
PYTHONPATH=src python3 -m wheelcontract wheelcontract.toml
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

`--wheel` requires one existing `.whl` file; it never interprets a project
directory as an override. Python 3.11+ uses the standard TOML parser. The Python
3.10 zero-dependency fallback intentionally accepts only this documented schema
and ordinary quoted strings, integers, booleans, and string arrays. It rejects
duplicate keys and sections consistently with the standard parser.

## Deliberate limits

JSON expectations distinguish booleans from numbers: `ready = true` rejects
JSON `1`, and an expected numeric `1` rejects JSON `true`. Numeric values
retain value equality, so JSON `1.0` satisfies an expected `1`. Strings do not
coerce to numbers. Mismatches are reported per field and fail the case.

When a case declares JSON expectations, bare `NaN`, `Infinity`, and `-Infinity`
make its stdout invalid even in nested or unasserted values. Such output fails
the case with exit 1. Quoted strings containing those words remain valid.
Python's default decoder accepts these extensions, so WheelContract rejects
them explicitly; see the [Python JSON documentation](https://docs.python.org/3/library/json.html#infinite-and-nan-number-values).

Output beyond the interpreter's JSON nesting limit fails that case with a
bounded diagnostic. Later cases still run; WheelContract does not increase the
decoder's recursion limit or abort the suite with a traceback.

- One Python project or wheel and one disposable environment per contract.
- No dependency resolution, environment matrix, shell, hooks, or arbitrary
  working-directory configuration.
- Process-tree cleanup applies to timed-out cases; commands that intentionally
  daemonize and exit successfully are outside the contract model.
- JSON assertions address top-level scalar fields only.
- Build isolation is disabled, so the invoking interpreter must already provide
  the project's declared build backend.

These boundaries keep WheelContract an artifact behavior check rather than a
tox/nox replacement. This repository exercises both the six-case AgentScope
contract at the portfolio root and the compact three-case self-contract in this
directory.

## Maintenance status

WheelContract v1.0.3 is a frozen local MVP. Its schema-v1 contract, exit
semantics, and synchronous process-lifecycle boundary remain stable. Resume
feature work only for a reproduced installed-artifact defect; use the focused
suite and portfolio validator as the release contract.

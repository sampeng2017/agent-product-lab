# WheelContract

WheelContract verifies the behavior users receive from an installed Python CLI
wheel. It builds a local project or accepts an existing `.whl`, installs that
single artifact without dependencies in a disposable virtual environment, and
runs explicit argument vectors from a small TOML contract.

The v0.3 prototype focuses on the release gap demonstrated by this portfolio:
source tests can pass while an installed command, JSON shape, or documented
policy exit has regressed.

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

Python 3.11+ uses the standard TOML parser. The Python 3.10 zero-dependency
fallback intentionally accepts only this documented schema and ordinary quoted
strings, integers, booleans, and string arrays.

## Deliberate limits

- One Python project or wheel and one disposable environment per contract.
- No dependency resolution, environment matrix, shell, hooks, or arbitrary
  working-directory configuration.
- Process-tree cleanup applies to timed-out cases; commands that intentionally
  daemonize and exit successfully are outside the contract model.
- JSON assertions address top-level scalar fields only.
- Build isolation is disabled, so the invoking interpreter must already provide
  the project's declared build backend.

These boundaries keep WheelContract an artifact behavior check rather than a
tox/nox replacement. The prototype should continue only if real dogfooding
shows its contract and diagnostics remain clearer than bespoke CI scripting.
This repository exercises both the six-case AgentScope contract at the portfolio
root and the compact three-case self-contract in this directory.

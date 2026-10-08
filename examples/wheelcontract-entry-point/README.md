# Passing source tests, missing installed command

A Python CLI's source tests pass, but its package metadata does not register
the console command. The wheel builds and installs successfully. Users then
cannot run the command promised by the project.

This example reproduces that release gap with real wheel builds. WheelContract
finds the missing command, then passes the same contract after the packaging
metadata is corrected. No assertion is weakened to make the result pass.

## Replay the example

[Install WheelContract](../../docs/INSTALLATION.md#wheelcontract-102) in a
Python 3.10+ environment and keep it active. This example builds a setuptools
project, so also install its declared build backend into that environment:

```sh
python -m pip install "setuptools>=77"
```

WheelContract disables build isolation when building a project. Its own
installation's isolated build environment does not guarantee the backend is
available when you later run it. The replay checks this prerequisite and never
installs or downloads dependencies itself.

From a current lab checkout:

```sh
python examples/wheelcontract-entry-point/demo.py
```

Pip-only users can obtain the example files while keeping their environment
active:

```sh
git clone https://github.com/sampeng2017/agent-product-lab.git
cd agent-product-lab
python examples/wheelcontract-entry-point/demo.py
```

The example lives on current `main`; the pinned installed WheelContract
revision predates it. The replay copies the project and contract to a temporary
directory, builds and tests there, changes only that copy, and removes its
wheels, build metadata, caches, and environments afterward.

Successful replay exits 0, including its expected installed-command failure.
Missing WheelContract or a suitable backend exits 2 with an installation hint.
Unexpected results exit 1. The fixture is intentionally broken at the start;
do not publish it as your own package.

## Why source tests pass

[`project/src/release_demo/cli.py`](project/src/release_demo/cli.py) implements
a greeting and `--version`. The two source tests call that function directly
and validate both behaviors. Source access is explicit through `PYTHONPATH=src`
for that test subprocess only; it does not prove an installed console command
exists.

The fixture's [`pyproject.toml`](project/pyproject.toml) has name, version,
source discovery, and build metadata, but no `[project.scripts]` entry.
The package therefore builds without providing `release-demo` as a command.

## Check what users install

The checked-in [`wheelcontract.toml`](wheelcontract.toml) declares two cases:

```toml
[[case]]
name = "greeting"
argv = ["release-demo"]
stdout_contains = ["hello from the installed wheel"]

[[case]]
name = "version"
argv = ["release-demo", "--version"]
stdout_contains = ["release-demo 1.0.0"]
```

WheelContract builds the project, installs the wheel in a new environment, and
resolves commands only from that environment. Its case processes have checkout
import variables removed. In the replay, this yields:

```text
$ wheelcontract wheelcontract.toml
FAIL greeting
  - installed command not found: release-demo
FAIL version
  - installed command not found: release-demo
Result: 0 passed, 2 failed, 2 total
Exit: 1
```

The build and install succeeded; the promised behavior is missing. This is
contract failure exit 1. Invalid configuration, build failure, and install
failure instead produce setup exit 2 from the WheelContract CLI.

## Correct the package metadata

The replay adds this entry to the temporary project's `pyproject.toml`:

```toml
[project.scripts]
release-demo = "release_demo.cli:main"
```

The standard mapping registers the command against the implemented function;
see the [PyPA entry-point specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/#entry-points).

The same contract then rebuilds and isolated-installs the corrected artifact:

```text
$ wheelcontract wheelcontract.toml
PASS greeting
PASS version
Result: 2 passed, 0 failed, 2 total
Exit: 0
```

The script checks both command exits and their diagnostics, including both
missing-command failures and both corrected passes. Its final line is:

```text
PASS: source tests passed -> installed command missing -> packaging corrected.
```

## Apply this release check to your CLI

Keep your own contract beside release fixtures. Name the command users install
and include a meaningful behavior case, not only `--help`. When checking an
already built artifact, run:

```sh
wheelcontract --wheel dist/your-package.whl path/to/wheelcontract.toml
```

For source builds, point `[artifact].source` at the project directory and make
the declared backend available to the invoking interpreter. Paths are relative
to the contract. The demo's displayed contract commands run in its temporary
copy; use replay to keep the checked-in intentionally broken fixture unchanged.

This sample has no runtime dependencies. WheelContract installs with `--no-deps`
and does not resolve application dependencies. See the
[WheelContract README](../../products/wheelcontract/README.md) for timeout,
output bounds, supported assertions, and the artifact's deliberate limits.

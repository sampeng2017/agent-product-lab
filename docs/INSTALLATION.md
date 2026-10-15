# Install a tool

Each maintained tool is a separate Python package. You can install just the one
you need and run it in your own project without cloning this lab or setting
`PYTHONPATH`.

You need Python 3.10 or newer, pip, Git on `PATH`, and network access to GitHub
and the Python package index for build dependencies. The tools have no runtime
dependencies. There are no published lab releases or package-index distributions
documented here; the commands below install directly from this public repository.

For new environments, prefer an upstream-maintained interpreter. The current
[coverage and lifecycle guidance](CI_PLATFORM.md#interpreter-coverage-and-lifecycle)
distinguishes Python 3.11–3.15 from the retained 3.10 compatibility floor.
Check the selected launcher with `python3 --version` on macOS/Linux or
`py -3 --version` on Windows before creating an environment. The commands below
use that launcher; they do not install or upgrade Python itself.

Want the CLI available across repositories without activating its environment?
Use the optional [pipx route](#install-cli-apps-with-pipx) instead of the tool
environment below. Your project's own test/application environment is separate.

## Create an environment

On macOS or Linux:

```sh
python3 -m venv .venv
. .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

Use a supported Python interpreter when creating the environment. After
activation, `python -m pip` and the installed commands use that environment.
If activation is unavailable, call `.venv/bin/python` and `.venv/bin/TOOL`
directly on macOS/Linux, or `.venv\Scripts\python.exe` and
`.venv\Scripts\TOOL.exe` on Windows. Keep the environment outside the tree you
are measuring, or ignore/exclude it in your project as appropriate.

## Choose one tool

| Your task | Tool | Installed command |
| --- | --- | --- |
| Check whether previous test evidence still applies after code changes | [ProofRun](../products/proofrun/README.md) | `proofrun` |
| Explain which repository instructions apply to a file | [AgentScope](../products/agentscope/README.md) | `agentscope` |
| Test a Python CLI as users receive it in a wheel | [WheelContract](../products/wheelcontract/README.md) | `wheelcontract` |
| Catch conflicting current-version claims in code and docs | [ReleaseFact](../products/releasefact/README.md) | `releasefact` |
| Find files a command creates, modifies, or removes, including ignored files | [ResidueCheck](../products/residuecheck/README.md) | `residuecheck` |
| Check an existing wheel's metadata, exact payload, and internal integrity | [WheelFact](../products/wheelfact/README.md) | `wheelfact` |

Run only the install command for the tool you choose. Most commands pin source
to public commit `84e76faa7f837a858fe6b6efdea9da8c24856b99`, whose portfolio CI
passed Python 3.10–3.14 when selected. Current compatibility coverage extends
through 3.15, with unchanged runtime/build definitions at the pins below. The
full revision keeps the source selection stable as
`main` evolves; it is not a release tag or a pin of pip's build dependencies.
WheelContract instead uses the validated v1.0.5 revision
`73a5e143cf4f2a1840f40a55912afea866b8fdd6` to include its assertion and
launch-error fixes.

### ProofRun 1.8.1

```sh
python -m pip install "proofrun @ git+https://github.com/sampeng2017/agent-product-lab.git@84e76faa7f837a858fe6b6efdea9da8c24856b99#subdirectory=products/proofrun"
proofrun --help
```

In your own Git repository, preview the detected test command before creating
a manifest. `init` refuses to overwrite existing files by default:

```sh
proofrun init --dry-run
proofrun init
proofrun verify
proofrun status --require-valid
proofrun audit
```

If detection is ambiguous, provide your verification command explicitly, for
example `proofrun init -- python -B -m unittest discover -s tests -v` for a
project with unittest tests. Checks must leave Git-visible inputs unchanged.
Changing code after verification makes the corresponding proof stale.

The [stale-proof worked example](../examples/proofrun-stale-proof/README.md)
provides a replayable project and explains the expected exit-1 result before
fresh verification restores the status gate.

### AgentScope 1.0.0

```sh
python -m pip install "agentscope-cli @ git+https://github.com/sampeng2017/agent-product-lab.git@84e76faa7f837a858fe6b6efdea9da8c24856b99#subdirectory=products/agentscope"
agentscope --version
```

From the repository you want to inspect, substitute your target file for
`src/app.py`. A planned file that does not exist yet is allowed:

```sh
agentscope --root . src/app.py
agentscope compare --root . src/app.py
```

The profiles model the documented subset of `agents-md` and `copilot-cli` in
the product README. Review that boundary before interpreting profile results
as client behavior.

The [instruction-scope worked example](../examples/agentscope-rule-scope/README.md)
shows an ignored `applyTo` rule, an explicit policy failure, and the coverage
after correcting its target pattern.

<a id="wheelcontract-100"></a>
<a id="wheelcontract-101"></a>
<a id="wheelcontract-102"></a>
<a id="wheelcontract-103"></a>
<a id="wheelcontract-104"></a>

### WheelContract 1.0.5

```sh
python -m pip install "wheelcontract-cli @ git+https://github.com/sampeng2017/agent-product-lab.git@73a5e143cf4f2a1840f40a55912afea866b8fdd6#subdirectory=products/wheelcontract"
wheelcontract --version
```

To upgrade an older environment, add `--upgrade` to that command.
Version 1.0.2 rejects bare NaN/Infinity/-Infinity in JSON assertion output and
retains the boolean/number correction from 1.0.1. Numeric value equality and
quoted strings remain compatible. Old section anchors remain available for
links from previously installed documentation.
Version 1.0.3 also reports decoder nesting failures per case and continues the
remaining checks, without raising the interpreter's recursion limit.
Version 1.0.4 also reports OS launch failures for installed commands that exist
but cannot start. Later checks still run and the suite returns behavior exit 1.
Version 1.0.5 rejects malformed UTF-8 in JSON assertion output before parsing;
valid Unicode, literal U+FFFD, and human-output previews remain compatible.

Create a contract using the [product example](../products/wheelcontract/README.md#contract),
then name your existing wheel:

```sh
wheelcontract --wheel dist/example.whl wheelcontract.toml
```

If you ask WheelContract to build a project instead, its invoking interpreter
must provide that project's build backend. WheelContract disables build
isolation and installs the artifact without resolving its runtime dependencies.

The [missing-command worked example](../examples/wheelcontract-entry-point/README.md)
builds a real sample wheel whose source tests pass, diagnoses its missing console
entry point, and rebuilds successfully after a metadata correction. It explicitly
requires the sample's build backend in the invoking environment.

The [installed-wheel CI guide](WHEEL_RELEASE_CI.md) carries that check into your
own GitHub repository with a copyable, non-publishing workflow. Review its
setuptools and zero-runtime-dependency boundary before adopting it.

### ReleaseFact 1.0.0

```sh
python -m pip install "releasefact @ git+https://github.com/sampeng2017/agent-product-lab.git@84e76faa7f837a858fe6b6efdea9da8c24856b99#subdirectory=products/releasefact"
releasefact --version
```

Create `releasefact.toml` from the [product example](../products/releasefact/README.md#contract)
with your own canonical version file and explicit current claims, then run:

```sh
releasefact releasefact.toml
```

### ResidueCheck 1.0.0

```sh
python -m pip install "residuecheck-cli @ git+https://github.com/sampeng2017/agent-product-lab.git@84e76faa7f837a858fe6b6efdea9da8c24856b99#subdirectory=products/residuecheck"
residuecheck --version
```

From your project, this no-op checks the tree without intentionally creating
files. Replace the command after `--` with the operation you want to measure:

```sh
residuecheck --root . --exclude .venv -- python -c "print('checked')"
```

A command that creates output will return exit 1 and name the residue. Exclude
dependency trees explicitly if the default scan bounds are too small.

### WheelFact 1.0.3

```sh
python -m pip install "wheelfact @ git+https://github.com/sampeng2017/agent-product-lab.git@84e76faa7f837a858fe6b6efdea9da8c24856b99#subdirectory=products/wheelfact"
wheelfact --version
```

Create a contract from the [product example](../products/wheelfact/README.md#contract)
and supply the wheel you want to check:

```sh
wheelfact wheelfact.toml dist/example-1.0.0-py3-none-any.whl
```

## Install CLI apps with pipx

Use this alternative for day-to-day command-line use, not project library
imports or editable development. Install [pipx](https://pipx.pypa.io/stable/)
first and make its app directory available on your PATH using its
[path setup guide](https://pipx.pypa.io/stable/how-to/configure-paths.html).
No project-local tool environment or lab checkout is needed. Do not use sudo.

Check `pipx --version` and choose an installed, maintained Python interpreter.
The examples use `python3.11`; replace that executable if needed. Keep the
entire quoted source requirement from the chosen tool's section. For example,
choose either of these, not a same-named package from an index:

```sh
pipx install --python python3.11 "proofrun @ git+https://github.com/sampeng2017/agent-product-lab.git@84e76faa7f837a858fe6b6efdea9da8c24856b99#subdirectory=products/proofrun"
proofrun --help
```

```sh
pipx install --python python3.11 "wheelcontract-cli @ git+https://github.com/sampeng2017/agent-product-lab.git@73a5e143cf4f2a1840f40a55912afea866b8fdd6#subdirectory=products/wheelcontract"
wheelcontract --version
```

The same prefix works with the other four quoted requirements above. All six
were installed and their exposed commands checked using pipx 1.7.1 with Python
3.11 on macOS. Windows pipx installation and newer backend combinations were
not live-tested here. A source pin still does not pin build dependencies.

### Use the app, not its environment as your project

Run the exposed CLI from your own repository. ProofRun's verification command
still needs your project's interpreter/dependencies, for example:

```sh
proofrun init --dry-run -- python3.11 -B -m unittest discover -s tests -v
proofrun init -- python3.11 -B -m unittest discover -s tests -v
proofrun verify
proofrun status --require-valid
```

Substitute your real project command; review the preview first. pipx isolates
ProofRun itself, not the commands it records. Activate your project's environment
when its tests need one. Do not inject project test dependencies into ProofRun
and assume its child commands will use them.

For an existing wheel, WheelContract's normal `--wheel` command needs no source
build backend in the tool environment. If asking it to build a setuptools
project, install pip and that backend into the **checker** environment first:

```sh
pipx inject wheelcontract-cli pip "setuptools>=77"
wheelcontract path/to/wheelcontract.toml
```

Use the project's declared backend instead of setuptools when appropriate.
Installing these packages into an unrelated project environment is not enough.
Injection does not add runtime dependencies to the isolated target wheel;
WheelContract still installs that target with `--no-deps`.

The Python-driven replay scripts use their calling interpreter's modules.
For those replays, use the activated-environment route above; merely exposing
a pipx command does not make `python -m TOOL` importable in another interpreter.

### Inspect, replace, or remove an app

```sh
pipx list
pipx runpip wheelcontract-cli check
pipx uninstall wheelcontract-cli
```

Management uses the distribution name before `@` in the requirement, not always
the CLI name: `wheelcontract-cli` exposes `wheelcontract`, `agentscope-cli`
exposes `agentscope`, and `residuecheck-cli` exposes `residuecheck`.
Uninstall removes the managed app, not your repository or ProofRun receipts.

To select a different source revision, edit the full hash in the quoted
requirement and use `pipx install --force` with that full requirement. This
updates the selected managed app and exposed commands; inspect `pipx list`
first. Keep the full hash unless you deliberately intend development tracking.
For interpreter changes, consult pipx's reinstall options rather than assuming
an install will switch an existing environment's Python.

References: [pipx CLI](https://pipx.pypa.io/stable/reference/cli.html) and
[injecting packages](https://pipx.pypa.io/stable/how-to/inject-packages.html).

## Install from a checkout instead

Clone the repository, select a revision, then install one product directory:

```sh
git clone https://github.com/sampeng2017/agent-product-lab.git
cd agent-product-lab
git checkout 84e76faa7f837a858fe6b6efdea9da8c24856b99
python -m pip install ./products/proofrun
```

That revision is the tested source for ProofRun and the other tools except
WheelContract. For WheelContract 1.0.5, select its correction revision before
installing; merely changing the product directory above would install 1.0.0:

```sh
git checkout 73a5e143cf4f2a1840f40a55912afea866b8fdd6
python -m pip install ./products/wheelcontract
wheelcontract --version
```

For the other tools, retain the first revision and replace `proofrun` with the
chosen product directory. For development, use
`python -m pip install -e ./products/proofrun` and follow its focused test
instructions. Installing from the repository root fails because the root is a
portfolio, not a Python package.

## Updates and troubleshooting

To follow development, replace the revision in a selected VCS command with
`main` and add `--upgrade`. That installs the branch state at the time pip runs;
use an explicit revision when you need stable source selection. If code changed
without a package-version bump, use `--force-reinstall` to refresh the installed
artifact at the selected revision.

- **Command not found:** activate the same environment used for installation,
  or use its command path directly. `python -m TOOL --help` also works.
- **Unsupported Python:** create the environment with Python 3.10 or newer.
- **Root is not installable:** use the product directory or retain the
  `#subdirectory=products/TOOL` fragment in the quoted VCS requirement.
- **TLS, proxy, or authentication error:** check access to GitHub and your
  package index and configure your organization's trusted CA/proxy settings.
  A public repository requires no GitHub token; build dependencies still need
  index access unless already available through an approved offline workflow.

The VCS syntax follows [pip's documentation](https://pip.pypa.io/en/stable/topics/vcs-support/).
Environment creation and activation follow [Python's venv documentation](https://docs.python.org/3/library/venv.html).

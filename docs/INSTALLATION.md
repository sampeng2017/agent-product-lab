# Install a tool

Each maintained tool is a separate Python package. You can install just the one
you need and run it in your own project without cloning this lab or setting
`PYTHONPATH`.

You need Python 3.10 or newer, pip, Git on `PATH`, and network access to GitHub
and the Python package index for build dependencies. The tools have no runtime
dependencies. There are no published lab releases or package-index distributions
documented here; the commands below install directly from this public repository.

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
passed Python 3.10–3.14. The full revision keeps the source selection stable as
`main` evolves; it is not a release tag or a pin of pip's build dependencies.
WheelContract instead uses the validated v1.0.2 revision
`09617c324310229972567e71e4a477edbc7161a5` to include its JSON assertion fixes.

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

### WheelContract 1.0.2

```sh
python -m pip install "wheelcontract-cli @ git+https://github.com/sampeng2017/agent-product-lab.git@09617c324310229972567e71e4a477edbc7161a5#subdirectory=products/wheelcontract"
wheelcontract --version
```

To upgrade an existing 1.0.0/1.0.1 environment, add `--upgrade` to that command.
Version 1.0.2 rejects bare NaN/Infinity/-Infinity in JSON assertion output and
retains the boolean/number correction from 1.0.1. Numeric value equality and
quoted strings remain compatible. Old section anchors remain available for
links from previously installed documentation.

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

## Install from a checkout instead

Clone the repository, select a revision, then install one product directory:

```sh
git clone https://github.com/sampeng2017/agent-product-lab.git
cd agent-product-lab
git checkout 84e76faa7f837a858fe6b6efdea9da8c24856b99
python -m pip install ./products/proofrun
```

Replace `proofrun` with another product directory from the table above. For
development, use `python -m pip install -e ./products/proofrun` and follow its
focused test instructions. Installing from the repository root fails because
the root is a portfolio, not a Python package.

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

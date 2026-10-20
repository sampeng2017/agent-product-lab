# Check your installed CLI in GitHub Actions

Source tests can pass while the wheel users install lacks its command. Add an
installed-behavior check beside your existing tests, before any publication
step. The check builds one wheel and gives that exact artifact to WheelContract;
it does not rebuild the project during the contract run.

This starter is for a setuptools-based Python CLI with **no runtime
dependencies**. It uses Python 3.11 on Ubuntu 24.04. WheelContract installs the
target wheel with `--no-index --no-deps` in a separate environment: installing
your application's dependencies in the outer job does not make them available
to its case commands. If your CLI requires third-party packages, this starter
does not model its installed environment; use a dependency-aware runner instead.

## Add the check to your project

1. Copy [wheelcontract-ci.yml](templates/wheelcontract-ci.yml) to
   `.github/workflows/wheelcontract.yml` in your repository. The template is
   not an active workflow in this lab.
2. Keep a `wheelcontract.toml` at your project root. Start with the contract
   below, replacing the command and output with behavior your CLI promises.
3. Keep your source tests. Review and commit both files, then inspect the
   `Installed CLI contract` result on a push or pull request.

```toml
schema_version = 1

[artifact]
source = "."

[run]
timeout_seconds = 10
max_output_bytes = 4096

[[case]]
name = "greeting"
argv = ["release-demo"]
stdout_contains = ["hello from the installed wheel"]

[[case]]
name = "version"
argv = ["release-demo", "--version"]
stdout_contains = ["release-demo 1.0.0"]
```

These two cases match the existing
[missing-command example](../examples/wheelcontract-entry-point/README.md).
For your project, include at least one useful operation, not only `--version`.
The [full contract reference](../products/wheelcontract/README.md#contract)
covers explicit failure exits, stderr, JSON fields, and `{manifest_dir}` fixtures.

## What the workflow checks

- The outer job installs setuptools and the tested
  [WheelContract 1.0.6 revision](INSTALLATION.md#wheelcontract-106).
- `pip wheel` builds the project into a fresh temporary directory. Exactly one
  `.whl` must exist, so a stale wheel in your repository's `dist/` cannot be
  selected accidentally.
- `--wheel` selects that artifact, regardless of `[artifact].source`. Its
  case commands run outside the checkout with Python import-leak variables
  removed. The source checkout is not the application import path.
- A failed contract makes the step fail; there is no `continue-on-error` or
  shell fallback that turns it into success. The exit trap removes temporary
  wheel output on normal completion and ordinary failure; a forcibly killed
  job cannot guarantee that shell cleanup runs. Nothing is uploaded, published,
  or pushed.

The missing-command fixture produces:

```text
FAIL greeting
  - installed command not found: release-demo
FAIL version
  - installed command not found: release-demo
Result: 0 passed, 2 failed, 2 total
```

After its packaging correction, the same workflow step and unchanged contract
produce two passes. Exit 1 means behavior differed; exit 2 from WheelContract
means invalid manifest or artifact setup. A failure from the preceding `pip
wheel` command is a build failure, not a WheelContract case result.
If the build succeeds but produces zero or multiple wheels, the starter reports
`Expected exactly one built wheel.` and exits 2 before invoking the checker.

## Adapt the starter deliberately

- For a project below the repository root, change the `.` argument to `pip
  wheel` and the contract path in the final command. Fixture paths remain
  relative to the contract through `{manifest_dir}`.
- For a different build backend, replace the setuptools installation with
  your declared backend requirements. Build isolation is disabled here;
  pip does not provision a separate build environment.
- Retain the quoted VCS requirement and full source revision. This pins
  WheelContract's source. The two official actions also use full commits,
  resolved from their v7 tags and matched to the lab's successful CI baseline.
  Build dependencies and the runner image's patch level are not pinned.
  Review and test deliberate updates to these selections.
- Add the check to an existing build job by passing its actual wheel instead
  of rebuilding. Do not silently choose the first of several artifacts.
- Configure required checks separately if you want merge protection. Merely
  adding this file does not change branch rules or gate another publishing job.

The template uses ordinary `pull_request`, read-only repository permissions,
and checkout without retained credentials. Building and running a submitted
package still executes its code; a disposable environment is not a sandbox.
Do not move this job into a privileged `pull_request_target` context or supply
secrets to untrusted pull requests. These choices follow
[GitHub's secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use).

The exact build/check shell block was rehearsed locally with the pinned
installed checker against the broken and corrected real fixture. The lab's
separate portfolio CI verifies the checker on Python 3.10–3.15; it is not a
hosted run of this external-project template. Windows and other backends are
not claimed by this starter.

Workflow placement and Python setup follow
[GitHub's Python workflow guide](https://docs.github.com/en/actions/tutorials/build-and-test-code/python).
Build options follow [pip wheel's reference](https://pip.pypa.io/en/stable/cli/pip_wheel/).

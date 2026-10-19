# Recover from rejected or stale ProofRun evidence

Tests passing and evidence still applying are different claims. ProofRun can
reject a successful command if it changes Git-visible inputs, or mark an earlier
passing result stale after an edit, commit, or age limit. Diagnose the reason
before rerunning, changing exclusions, or changing the age policy.

These commands use installed [ProofRun 1.8.1](INSTALLATION.md#proofrun-181),
the default store, and a check named `unit`. Run them from the same project
directory as verification. Substitute your check name; `init` names its default
check `test`. For a custom store, put `--store PATH` before each subcommand.

## Start with the recorded reason

```sh
proofrun status --require-valid unit
proofrun status --json unit
git status --short --untracked-files=all
```

These inspections do not run tests or create new receipts. The first command
exits 1 for stale or missing evidence; status without `--require-valid` remains
informational and can exit 0 for the same stale result. A setup error exits 2:
check the diagnostic, working directory, store, and check name first.

| Reason | What to do next |
| --- | --- |
| `no receipt` / `MISSING` | Check the name and store. Run the intended check; status itself does not verify. |
| `failed` | Read the test/command failure and `receipt.command_exit_code`. Fix it, then verify again. |
| `repository changed during check` | Inspect the receipt's mutation paths. Move intentional edits before verification. |
| `working tree changed` or `commit changed` | Review the edits or new commit, then verify the intended current state. A clean Git status alone does not restore old evidence. |
| `expired` | Run fresh verification. Change the age policy only if that is the policy you intend to enforce. |
| `receipt chain invalid` | Preserve the store and investigate integrity; do not delete entries or rewrite hashes to make the gate pass. |

Multiple reasons can apply at once. `proofrun audit` checks receipt hashes and
links, not whether old evidence applies to today's code. Conversely, a clean
audit does not fix a failed test or stale proof.

## Tests passed, but the check changed files

For example, a formatter or generator can finish successfully while changing
`calculator.py`. Human status then includes:

```text
STALE  unit: repository changed during check: calculator.py
```

In `status --json unit`, inspect these fields in the selected item's receipt:

```text
receipt.command_exit_code                   0
receipt.exit_code                           1
receipt.repository_mutation.detected        true
receipt.repository_mutation.tracked_paths   ["calculator.py"]
```

The command passed; its proof was rejected. Mutation `tracked_paths` and
`untracked_paths` describe changes during the check. The separate top-level
`working_tree_paths` describes later drift and can be empty in this case.

Run your formatter/generator separately, review its changes, then run only the
verification check against that resulting state. Remove mutating steps from the
check's manifest command; merely rerunning an idempotent generator is not a
durable fix. For a `unit` check that now runs tests without editing inputs:

```sh
proofrun verify --jobs 1 unit
proofrun status --require-valid unit
proofrun audit
```

Use sequential checks while diagnosing shared-file changes. Parallel checks
can observe each other's writes. The manifest command still needs your project
dependencies; installing ProofRun with pipx does not install your test runner.
A command named `python` resolves on inherited PATH. Activate the intended
project environment or use its explicit executable path in the manifest.
Invoking a virtual environment's Python by absolute path does not activate
that environment for other commands.

For Python, `python -B` suppresses bytecode writes. For pytest, consider
`python -B -m pytest -p no:cacheprovider` if disabling its cache fits your tests;
the [cache plugin documentation](https://docs.pytest.org/en/stable/how-to/cache.html)
describes that tradeoff. Other plugins and tests can still write files. Inspect
the reported paths rather than assuming all generated files are harmless.

Do not ignore source files to obtain a green gate. If a cache/output is
intentionally outside the evidence boundary, review that decision explicitly.
Git ignores do not exclude already-tracked files; see the
[Git ignore rules](https://git-scm.com/docs/gitignore). ProofRun does not detect
ignored-file mutations or transient edits restored before the check finishes.

## A report or JSON export made proof stale

Creating `proofrun-report.md` in the project root adds a Git-visible input
unless it is ignored. Overwriting a tracked report changes an input too. The
report describes the state before its output file is written; a report command
exiting 0 is not a validity gate.

For terminal inspection, avoid creating a file:

```sh
proofrun report
```

For saved exports after verification, the default `.proofrun/` directory has
an ignore file. Confirm it is still ignored and not already tracked:

```sh
git check-ignore -v -- .proofrun/report.md .proofrun/status.json
git ls-files -- .proofrun
```

The first command should show applicable ignore rules; the second should print
no tracked evidence files. If those conditions do not hold, use a location
outside the project instead. Do not untrack or delete user files automatically.
With the default ignored directory, save and then check validity separately:

```sh
proofrun report --output .proofrun/report.md
proofrun status --json unit > .proofrun/status.json
proofrun status --require-valid unit
```

Review any existing root export before moving it outside the measured tree.
If it was the only drift, restoring the earlier input state can make existing
proof valid again; otherwise review remaining reasons and verify anew.
Do not delete receipts as a workaround. Reports include commands, paths, and
configured environment values; review them before sharing and never put secrets
in manifest environment overrides.

## Keep the evidence when you need more detail

```sh
proofrun history --json --limit 5
proofrun audit
```

History distinguishes the latest failed or rejected attempt from an older pass.
An unreadable store is a setup problem; a readable but damaged sealed chain
fails audit. New verification does not repair earlier chain damage. There is no
automatic repair command, and hash consistency is not authentication against
someone who can rewrite the whole store.

To see normal edit-then-reverify behavior without changing your project,
[replay the existing disposable example](../examples/proofrun-stale-proof/README.md).
See the [product reference](../products/proofrun/README.md) for manifests,
JSON output, age settings, and the full evidence boundary.

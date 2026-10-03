# When passing tests become stale evidence

You run tests, then edit code. The test result is still recorded as passing,
but it describes the earlier working tree. ProofRun identifies that gap and
requires fresh verification before its status gate passes again.

This example changes `double(value)` from `value * 2` to `value + value`.
Both implementations pass the same tests. The rejected status means the old
evidence is stale; it does not mean that ProofRun found a code defect.

## Replay the example

[Install ProofRun](../../docs/INSTALLATION.md#proofrun-181) and use that Python
environment. You also need Git on PATH and a checkout of this repository for
the example files. From the lab root:

```sh
python examples/proofrun-stale-proof/demo.py
```

If you installed through pip and do not have the example files, keep your
environment active and clone the current lab:

```sh
git clone https://github.com/sampeng2017/agent-product-lab.git
cd agent-product-lab
python examples/proofrun-stale-proof/demo.py
```

The example files are on current `main`; the older installation revision in
the install guide predates this example. Cloning the lab does not change the
installed ProofRun version used by the replay.

The script copies the small project into a temporary directory, initializes
Git there, and runs installed ProofRun. It never edits your checkout, commits
to your repository, or changes your Git identity settings. The temporary copy
and its receipts are removed when the demonstration ends. Each replay starts
with fresh evidence, so you can run it repeatedly.

The script checks the command exits and JSON status, including the changed
`calculator.py` path. An expected stale status is part of a successful demo.
The script exits 0 after the complete sequence, 2 if Git or installed ProofRun
is missing, and 1 if a step gives an unexpected result.

## Read the results

First, `proofrun verify unit` executes the unittest command in
[`project/proofrun.toml`](project/proofrun.toml). The subsequent gate passes:

```text
$ proofrun status --require-valid unit
VALID  unit: evidence applies
Exit: 0
```

After the edit, the same gate names the changed file and fails:

```text
$ proofrun status --require-valid unit
STALE  unit: working tree changed: calculator.py
Exit: 1
```

Run `proofrun verify unit` again. The edited code passes its tests and a new
receipt now covers that working tree. The gate returns to `VALID` and exit 0;
`proofrun audit` verifies both receipt hashes and their chain links.

The final line is:

```text
PASS: valid -> stale -> valid; all changes stayed in the temporary copy.
```

Receipt IDs and test duration vary. A valid audit means the recorded chain is
internally consistent; it does not make old evidence applicable to new code.

## Use the pattern in your project

Create a manifest with your actual verification command, or preview detection
with `proofrun init --dry-run`. Before relying on previous test evidence, run:

```sh
proofrun status --require-valid unit
```

If it returns `STALE`, read the reason and run `proofrun verify unit` for the
current inputs. Substitute your check's name for `unit`. Adding only the status
gate does not run tests. A verifier must leave Git-visible inputs unchanged;
this demo disables bytecode with `python -B` and ignores `.proofrun/`.

See the [ProofRun README](../../products/proofrun/README.md) for named checks,
age limits, JSON output, manifest contexts, and the receipt threat boundary.

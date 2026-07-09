# ProofRun

ProofRun is a local-first verification receipt tool for developers working with
AI coding agents. It runs a check, records the result together with the current
Git state, and later tells you whether that evidence still applies to the code
in front of you.

The first prototype is dependency-free and intentionally small. Receipts stay
inside the repository under `.proofrun/` and are ignored by Git.

## Quick start

ProofRun requires Python 3.10 or newer.

```bash
python3 -m proofrun run --name unit-tests -- python3 -m unittest discover -s tests
python3 -m proofrun status
python3 -m proofrun history
```

For development from this checkout, either install it in editable mode or set
`PYTHONPATH`:

```bash
PYTHONPATH=src python3 -m proofrun run --name unit-tests -- \
  python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m proofrun status
```

`status` marks a successful receipt as `valid` only while all of these remain
true:

- the receipt is newer than the selected maximum age;
- the Git commit is unchanged;
- tracked changes and untracked file contents are unchanged.

Use `--max-age-hours 0` to disable the age limit and `--json` for
machine-readable output.

## Why this exists

AI agents can generate code quickly, but a claim like "tests passed" becomes
stale as soon as the working tree changes. ProofRun turns that claim into a
small, inspectable receipt tied to a concrete repository state. See
[`docs/PRODUCT.md`](docs/PRODUCT.md) for the product exploration and roadmap.

## Development

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The project uses only the Python standard library.

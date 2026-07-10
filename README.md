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
cat > proofrun.toml <<'EOF'
[checks.unit]
command = ["/bin/sh", "-c", "PYTHONPATH=src python3 -m unittest discover -s tests -v"]
EOF

PYTHONPATH=src python3 -m proofrun verify
PYTHONPATH=src python3 -m proofrun status
PYTHONPATH=src python3 -m proofrun audit
PYTHONPATH=src python3 -m proofrun history
```

For development from this checkout, either install it in editable mode or set
`PYTHONPATH`:

```bash
PYTHONPATH=src python3 -m proofrun run --name unit-tests -- \
  python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m proofrun verify unit
PYTHONPATH=src python3 -m proofrun status --json
```

`status` marks a successful receipt as `valid` only while all of these remain
true:

- the receipt is newer than the selected maximum age;
- the Git commit is unchanged;
- tracked changes and untracked file contents are unchanged.

Use `--max-age-hours 0` to disable the age limit and `--json` for
machine-readable output. When a receipt goes stale because the working tree
drifted, `status` names the tracked and untracked paths that changed when that
detail is available in the recorded receipt.

`verify` runs checks from `proofrun.toml` and records one receipt per check. The
manifest currently uses `[checks.<name>]` tables with a `command` string array.

Every new receipt is sealed with a SHA-256 digest and links to the digest of the
previous entry. `proofrun audit` verifies those hashes and links, reports older
unsealed receipts without rejecting them, and exits nonzero if it finds a
broken chain. `status` also marks proof downstream of a chain failure as stale.
This makes accidental or undisclosed edits evident; it is not a digital
signature and does not protect against an attacker who can rewrite the entire
local store.

## Why this exists

AI agents can generate code quickly, but a claim like "tests passed" becomes
stale as soon as the working tree changes. ProofRun turns that claim into a
small, inspectable receipt tied to a concrete repository state. See
[`docs/PRODUCT.md`](docs/PRODUCT.md) for the product exploration and roadmap.

## Development

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m proofrun verify
```

The project uses only the Python standard library.

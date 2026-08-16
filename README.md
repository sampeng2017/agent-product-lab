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
PYTHONPATH=src python3 -m proofrun report --output proofrun-report.md
PYTHONPATH=src python3 -m proofrun history
```

For development from this checkout, either install it in editable mode or set
`PYTHONPATH`:

```bash
PYTHONPATH=src python3 -m proofrun run --name unit-tests -- \
  python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m proofrun verify unit
PYTHONPATH=src python3 -m proofrun verify --jobs 4
PYTHONPATH=src python3 -m proofrun verify --json
PYTHONPATH=src python3 -m proofrun status --json
PYTHONPATH=src python3 -m proofrun status --path-limit 5
PYTHONPATH=src python3 -m proofrun status --require-valid unit
```

`status` marks a successful receipt as `valid` only while all of these remain
true:

- the receipt is newer than the selected maximum age;
- the Git commit is unchanged;
- tracked changes and untracked file contents are unchanged.

Repository metadata and changed-path discovery use one NUL-safe Git status
snapshot. Untracked contents are still hashed exactly, in bounded-memory
chunks, so performance remains proportional to the bytes covered without
weakening drift detection or changing existing receipt fingerprints.
Tracked working-tree and staged patches are collected in batches and split into
their original per-path byte ranges, reducing the normal tracked-change path to
five Git subprocesses regardless of file count. If unusual Git output cannot be
split safely, ProofRun falls back to exact per-path diffing.

Use `--max-age-hours 0` to disable the age limit and `--json` for
machine-readable output. When a receipt goes stale because the working tree
drifted, `status` names up to 10 tracked and untracked paths that changed, then
reports how many more were omitted. Set `--path-limit N` to change that display
limit or `--path-limit 0` to show only the overflow count. JSON output always
contains the complete path lists regardless of the display limit.

Use `status --require-valid [NAME...]` as an acceptance gate for an agent or CI
job. With names, ProofRun assesses only those checks in the requested order and
reports `missing` when a name has no receipt. Without names, it requires every
latest receipt to be valid and rejects an empty store. The command exits 0 only
when every selected proof is valid, 1 when any proof is stale or missing, and 2
for malformed input or an unreadable store. Without `--require-valid`, status
remains informational and exits 0. The same contract applies with `--json`.

`verify` runs checks from `proofrun.toml` and records one receipt per check. It
runs sequentially by default; use `--jobs N` to run at most `N` checks at once.
Results are summarized in manifest order even when checks finish in a different
order, while receipts are appended in their actual completion order. With
`--fail-fast`, ProofRun stops launching checks after it observes a failure;
checks already running finish and still record receipts. A check can set a
repository-relative working directory and explicit environment overrides in
addition to its command:

```toml
[checks.api]
command = ["python3", "-m", "unittest", "discover", "-s", "tests"]
cwd = "packages/api"

[checks.api.env]
APP_MODE = "test"
PYTHONPATH = "src"
```

Use `verify --json` for agent and CI consumption. Standard output contains one
versioned JSON document with the suite state and exit code, selected, executed,
passed, failed, and skipped counts, skipped check names, and manifest-ordered
per-check results with their complete receipts. Check output is routed to
standard error in this mode so it cannot corrupt the JSON document. A failed
suite still exits with the first failing check's nonzero exit code.

`command` must be a non-empty string array, `cwd` cannot be absolute or escape
the repository, and every environment value must be a string. ProofRun validates
all selected check directories before it starts the suite. Commands inherit the
process environment, then apply these overrides. New receipts and Markdown
reports record the configured working directory and override values so the
execution context remains inspectable. Do not put secrets in the manifest: the
values are stored verbatim in local receipts and reports.

ProofRun snapshots Git immediately before and after every check. If a command
exits successfully but leaves the commit, tracked changes, or untracked files
changed, ProofRun rejects that proof with exit code 1. The schema-v5 receipt records
the command's real exit code, both Git snapshots, and the changed paths, so
`status`, JSON output, and Markdown reports can explain the rejection. A command
that already failed keeps its original nonzero exit code while retaining the
same mutation evidence. Run generators, formatters, and other intentional
mutators before a separate verification check; this ensures the receipt covers
code the verifier actually saw. In a parallel suite, one check can observe
another check's mutation, so use `--jobs 1` whenever commands may change shared
repository state. Mutations to ignored files and transient changes that are
fully restored before the command exits are outside this Git snapshot boundary.

Every new receipt is sealed with a SHA-256 digest and links to the digest of the
previous entry. `proofrun audit` verifies those hashes and links, reports older
unsealed receipts without rejecting them, and exits nonzero if it finds a
broken chain. `status` also marks proof downstream of a chain failure as stale.
This makes accidental or undisclosed edits evident; it is not a digital
signature and does not protect against an attacker who can rewrite the entire
local store.

Receipt writers are serialized with an OS-managed sibling lock file (for the
default store, `.proofrun/receipts.jsonl.lock`). The lock covers only the short
load, link, and append operation—not command execution—so simultaneous ProofRun
writers cannot fork the chain or interleave final-record writes. The operating
system releases the lock if a writer exits unexpectedly; the persistent lock
file is ignored alongside the local receipt store. Readers coordinate through
the same lock so they never parse a partially appended final record.

`proofrun report` exports the current assessment as Markdown for a code review
or agent handoff. It includes the repository state, evidence-age policy,
receipt-chain audit counts, and each check's latest result, command, execution
context, receipt, covered commit, and invalidating paths. The report is printed
to standard output by default; use `--output PATH` to write it to a file and
`--max-age-hours 0` to disable expiry. A damaged receipt chain is still
rendered, but the command exits nonzero so automation cannot silently publish
it as trusted evidence. Reports use the same 10-path default per check and
accept `--path-limit N`; omitted paths are counted explicitly. This limit is
presentation-only and never changes stored receipts or status JSON.

## GitHub Actions

The repository includes a working CI integration in
[`proofrun.yml`](.github/workflows/proofrun.yml). It installs ProofRun, saves
the versioned `verify --json` result, adds the Markdown report to the workflow
job summary, uploads both files as a 14-day `proofrun-evidence` artifact, and
then enforces the named `unit` proof with `status --require-valid`.

The report, artifact, and proof-gate steps use `always()` so they still run
after unsuccessful verification; the original failure remains part of the job
result. Both generated files live under GitHub's runner temp directory rather
than the checkout, because writing them into the repository during a check
could invalidate mutation-safe evidence. Use `proofrun init --github-actions`
to generate the same integration in another repository with an explicit
ProofRun install source.

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

## Bootstrap another repository

`proofrun init` detects a single Python, Node.js, Rust, or Go project and writes
a starter `proofrun.toml`. Python projects with pytest configuration use
`python -m pytest`; other repositories with a `tests/` directory use unittest.
For Node.js, ProofRun first requires a non-placeholder `scripts.test` entry,
then honors the `packageManager` declaration or a single npm, pnpm, Yarn, or Bun
lockfile. It defaults to npm only when no manager is declared or locked, and
rejects conflicting lockfiles instead of guessing. Mixed, ambiguous, or
unrecognized repositories must provide the intended command explicitly:

```bash
proofrun init --check-name unit -- python -m pytest -q
```

Existing targets are never overwritten unless `--force` is explicit. When CI
adoption is wanted, `--github-actions` also creates the proven evidence
workflow. It requires a real pip install requirement rather than guessing that
ProofRun is published at a particular location:

```bash
proofrun init \
  --github-actions \
  --ci-install "proofrun @ git+https://github.com/YOUR_ORG/proofrun.git@v1.7.0"
```

ProofRun validates the command choice and every selected destination before it
writes anything, so an existing manifest or workflow prevents a partial
scaffold. The generated workflow publishes structured JSON and a Markdown job
summary/artifact, audits the receipt chain, and requires all latest proofs to be
valid. For an automatically detected Node project, it also provisions the
selected runtime/package manager and installs project dependencies before
verification: Node.js 24 for npm, pnpm, and Yarn; the official pnpm setup action;
Corepack for Yarn; or the official Bun setup action. Existing lockfiles select
strict install modes such as `npm ci`, `pnpm install --frozen-lockfile`,
`yarn install --frozen-lockfile`, and `bun ci`.

Review the detected command and pin the ProofRun install requirement to a tag or
commit before committing the generated files. A `packageManager` declaration
also pins pnpm, Yarn, or Bun for their setup tool; lockfile-only projects use the
setup tool's current default, so add a declaration when exact package-manager
reproducibility matters. Explicit custom commands remain opaque and do not
receive inferred project setup.

Preview the same validation and file decisions without writing anything:

```bash
proofrun init --dry-run
proofrun init --dry-run --json -- python -m pytest -q
```

The human preview reports the detected or explicit command and whether each
target would be created or overwritten. The versioned JSON preview also includes
the exact generated content, making it suitable for agent review. `--force`
still controls whether existing targets may be previewed as overwrites, and
`--json` is accepted only with `--dry-run`, so structured preview cannot be
mistaken for an applied scaffold.

# ReleaseFact

ReleaseFact v1.0.0 is a dependency-free, read-only local MVP for Python
maintainers who repeat a current release version across package code, installed
behavior contracts, and documentation. It checks those explicit claims against
one canonical string in a TOML file and reports every drift in one run.

The prototype addresses a concrete portfolio failure: WheelContract's canonical
metadata had advanced to v0.3.0 while a portfolio page still called it v0.1.0.
ReleaseFact deliberately does not search for versions or decide whether a
historical mention is stale. Maintainers declare only current claims.

## Install

Use the [tested Git installation guide](../../docs/INSTALLATION.md#releasefact-100)
to install this package alone. Create a contract for your project using the
example below, then run `releasefact releasefact.toml` from your project.

## Contract

```toml
schema_version = 1

[canonical]
file = "pyproject.toml"
key = "project.version"

[[claim]]
name = "runtime version"
file = "src/example/__init__.py"
template = "__version__ = \"{version}\""

[[claim]]
name = "release documentation"
file = "README.md"
template = "Example v{version} is the current release."
```

The canonical value must be a non-empty TOML string addressed by a dotted key.
Every named claim uses an exact one-line template with one `{version}` slot and
must select exactly one line. Paths are relative to the contract and cannot
escape its directory, including through symlinks. Declaration order determines
report order.

```text
DRIFT runtime version: src/example/__init__.py:1 is '0.2.0'; expected '1.0.0'
DRIFT release documentation: README.md:1 is '0.1.0'; expected '1.0.0'
Result: canonical '1.0.0'; 0 matched, 2 drifted, 2 total
```

Exit 0 means every declared claim matches, 1 means release drift, and 2 means
the contract, canonical value, path, or selector is invalid. ReleaseFact never
edits a file.

## Run locally

```bash
PYTHONPATH=src python3 -m releasefact releasefact.toml
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The product contract dogfoods its runtime, README, and status claims. The root
portfolio contract adds root README, status, handoff, and product-index claims
and is run from the installed wheel. The test fixture under
`tests/fixtures/stale-release/`
models three independently stale claims and pins complete actual-versus-expected
diagnostics.

## Why retain the prototype

A focused shell can read `project.version` and `rg` known files, but it must
still encode three selectors, extract each actual value, preserve failures while
continuing, distinguish missing or ambiguous selectors from drift, and format a
summary. ReleaseFact's declaration keeps each stable selector beside its file
and centralizes those behaviors. The contract is slightly longer than three
search commands, but the tested all-mismatch diagnosis is materially clearer
and reusable. That met the bounded experiment's retention threshold.

## Deliberate limits

- One canonical TOML string and explicit one-line claims only.
- No recursive discovery, regexes, version semantics, historical-mention
  inference, replacement, or write mode.
- No generic configuration synchronization or non-TOML canonical sources.
- Python 3.10's dependency-free fallback resolves a basic quoted canonical
  string; Python 3.11+ uses the standard TOML parser.

## Release boundary

The v1.0.0 command, schema v1 contract, deterministic diagnostics, and exit
codes 0/1/2 are frozen. A disposable seven-claim version-bump rehearsal guided
every update and caught one initially missed documentation claim; the unchanged
contract then passed. The wheel contents, metadata, installed command, source
and installed contracts, Python 3.10 fallback, and error surfaces were audited
before this release. Reopen behavior only for a reproduced defect.

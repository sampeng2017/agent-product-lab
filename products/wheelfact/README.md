# WheelFact 1.0.3

WheelFact is a dependency-free, read-only CLI that checks one existing Python
wheel against an exact TOML contract. It compares distribution metadata,
console entry points, and every non-`.dist-info` payload member without building
or installing the artifact.

Use the [tested Git installation guide](../../docs/INSTALLATION.md#wheelfact-103)
to install this package alone. Declare your wheel's expected facts using the
contract below, then run the installed `wheelfact` command with that artifact.

The `license` fact accepts modern core-metadata `License-Expression` and falls
back to the legacy `License` header for existing wheels.

Before comparing contract facts, WheelFact verifies the wheel's complete
`RECORD`: every archive file except `RECORD` and deprecated signature files
must have a secure matching hash, every archive file must have the required
row, and each provided size must match. Invalid, duplicate, unsafe, weak-hash,
or stale entries are artifact errors (exit 2), not contract mismatches.

The package also exposes `verify_wheel_integrity(Path(...))` for a caller that
needs the same bounded structure and `RECORD` validation without declaring
exact metadata or payload expectations. The portfolio validator uses this
narrow library hook for every built wheel; the command-line interface remains
an exact-contract checker.

```bash
wheelfact wheelfact.toml dist/example-1.0.0-py3-none-any.whl
```

Matching artifacts exit 0, contract mismatches exit 1, and invalid contracts or
artifacts exit 2. Every mismatch is reported in one run. The schema deliberately
uses exact strings and member paths: WheelFact is an artifact contract, not a
general packaging linter, metadata policy engine, builder, installer, or repair
tool.

## Contract

```toml
schema_version = 1

[wheel]
distribution = "example-cli"
version = "1.0.0"
requires_python = ">=3.10"
license = "MIT"
package_members = [
  "example/__init__.py",
  "example/cli.py",
]

[wheel.console_scripts]
example = "example.cli:main"
```

`package_members` is the exact sorted set of archive files outside the wheel's
single `.dist-info` directory. Generated metadata files are intentionally not
listed. The checker caps the central directory at 10,000 entries, metadata
control files at 1 MiB, and total streamed `RECORD` verification at 1 GiB.

## Development

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m wheelfact --help
```

Version 1.0.3 is the frozen local MVP. Real contracts for ResidueCheck and
AgentScope exercise the same schema across two independent wheels, while the
contract-independent library hook protects all six portfolio artifacts. Its
exact CLI contract, integrity validation, diagnostics, bounds, and exit 0/1/2
behavior are stable. Reopen only for a demonstrated correctness or safety
defect, not inferred names, globs, build behavior, or installed-command checks.

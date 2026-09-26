# WheelFact 1.0.1

WheelFact is a dependency-free, read-only CLI that checks one existing Python
wheel against an exact TOML contract. It compares distribution metadata,
console entry points, and every non-`.dist-info` payload member without building
or installing the artifact.

The `license` fact accepts modern core-metadata `License-Expression` and falls
back to the legacy `License` header for existing wheels.

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
listed. The checker caps the central directory at 10,000 entries and metadata
control files at 1 MiB; it never decompresses package payloads.

## Development

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m wheelfact --help
```

Version 1.0.1 is the frozen local MVP. Real contracts for ResidueCheck and
AgentScope exercise the same schema across two independent wheels. Its exact
contract, diagnostics, bounds, and exit 0/1/2 behavior are stable. Reopen only
for a demonstrated correctness or safety defect, not inferred names, globs,
build behavior, or installed-command checks.

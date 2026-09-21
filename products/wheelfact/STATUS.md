# WheelFact status

## Product shape

WheelFact v0.1.0 is a retained bounded prototype. It reads one existing wheel
and checks exact scalar metadata, console scripts, and non-`.dist-info` payload
members against one strict TOML contract.

## Initial evidence

- The ResidueCheck v1.0.0 contract expresses four metadata facts, one console
  entry point, and four package modules without building or installing.
- Missing, unexpected, and unequal facts are distinct and all mismatches appear
  in one deterministic report.
- Artifact and contract failures use exit 2; clean and mismatching audits use
  exits 0 and 1.
- A focused assertion script is shorter for one artifact, but must duplicate
  archive validation, metadata parsing, entry-point parsing, set comparison,
  all-mismatch reporting, and exit semantics for each release audit.

## Boundaries

- No build, install, repair, PyPI access, metadata policy, filename inference,
  globs, or installed-behavior checks.
- Exact values are intentionally contract-owned; standard `.dist-info` members
  are not enumerated, while all payload members are.
- Archives are limited to 10,000 entries; only metadata and entry-point control
  files are decompressed, each under 1 MiB.

## Next decision

Exercise the contract against a second portfolio wheel with deliberately stale
metadata, entry-point, missing-member, and unexpected-member expectations. Keep
the schema only if those diagnostics remain clearer than the equivalent script.

# WheelFact status

## Product shape

WheelFact v1.0.1 is a frozen local MVP. It reads one existing wheel and checks
exact scalar metadata, console scripts, and non-`.dist-info` payload members
against one strict TOML contract.

## Release evidence

- The v1.0.1 maintenance release accepts the standard core-metadata
  `License-Expression` header produced by PEP 639 packaging metadata while
  retaining legacy `License` compatibility.

- The ResidueCheck v1.0.0 contract expresses four metadata facts, one console
  entry point, and four package modules without building or installing.
- Missing, unexpected, and unequal facts are distinct and all mismatches appear
  in one deterministic report.
- Artifact and contract failures use exit 2; clean and mismatching audits use
  exits 0 and 1.
- A focused assertion script is shorter for one artifact, but must duplicate
  archive validation, metadata parsing, entry-point parsing, set comparison,
  all-mismatch reporting, and exit semantics for each release audit.
- A second exact contract passes against AgentScope's larger independent wheel.
  A deliberately stale 16-line copy reported four scalar mismatches, missing
  and unexpected console scripts, and missing and unexpected payload members in
  one run; three still-correct members remained visible.
- The focused comparison script required 44 lines while omitting WheelFact's
  archive safety, ambiguity checks, read bounds, strict contract parsing, and
  stable setup-error behavior.

## Boundaries

- No build, install, repair, PyPI access, metadata policy, filename inference,
  globs, or installed-behavior checks.
- Exact values are intentionally contract-owned; standard `.dist-info` members
  are not enumerated, while all payload members are.
- Archives are limited to 10,000 entries; only metadata and entry-point control
  files are decompressed, each under 1 MiB.

## Decision

Freeze v1.0.1. The second-artifact rehearsal needed no schema change and made
every correction explicit. Keep exact schema v1 and exits 0/1/2 stable; reopen
only for a concrete correctness or safety defect.

# WheelFact status

## Product shape

WheelFact v1.0.3 is a frozen local MVP. It reads one existing wheel, verifies
its complete `RECORD`, and checks exact scalar metadata, console scripts, and
non-`.dist-info` payload members against one strict TOML contract.

## Release evidence

- The v1.0.1 maintenance release accepts the standard core-metadata
  `License-Expression` header produced by PEP 639 packaging metadata while
  retaining legacy `License` compatibility.
- The v1.0.2 maintenance release rejects missing or extra `RECORD` membership,
  weak, malformed, or unequal hashes, and unequal declared sizes before
  evaluating contract facts. Verification is streamed and capped at 1 GiB.
- Disposable AgentScope wheels proved the gap: pip 25.0.1, WheelContract 1.0.0,
  and Twine 7.0.0 accepted bad digest, bad size, missing-row, and unrecorded-file
  variants. `wheel unpack` 0.45.1 caught all but the false size, while pre-fix
  WheelFact caught only the unrecorded payload through exact membership.
- A focused 33-line standard-library verifier caught all four mutations but
  omitted WheelFact's safe paths, duplicates, strong-algorithm validation,
  decompression bounds, complete diagnostics, and stable artifact-error exit.
- The v1.0.3 maintenance release exposes the same bounded structure and
  `RECORD` validation as `verify_wheel_integrity` without adding a second CLI
  mode. Portfolio validation calls it for all six wheels while exact contracts
  remain focused on ResidueCheck and AgentScope.

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
- Archives are limited to 10,000 entries; metadata control files are capped at
  1 MiB, and payloads are streamed for `RECORD` verification with a 1 GiB
  aggregate uncompressed limit.

## Decision

Freeze v1.0.3. The demonstrated integrity blind spot justified a narrow
artifact-validation correction and portfolio-wide reuse without changing
schema v1, the exact-contract CLI, or exit semantics. Keep exact schema v1 and
exits 0/1/2 stable; reopen only for another concrete correctness or safety
defect.

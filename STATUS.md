# Product lab status

## Current direction

WheelFact v0.1.0 is retained as the sixth product prototype. The first five
local MVPs remain frozen. The prototype replaces repeated manual wheel release
audits with one exact, read-only artifact contract; the next run must test its
diagnostics against a second real portfolio wheel before promotion.
ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

## Product shape

- `products/wheelfact/` contains a dependency-free Python 3.10+ CLI and five
  focused tests.
- One strict TOML contract names distribution, version, Python requirement,
  license, console scripts, and exact non-`.dist-info` payload members.
- It reads an existing wheel only, caps archive entries and decompressed control
  files, and reports all missing, unexpected, and unequal facts.
- Clean, mismatching, and invalid checks use exits 0, 1, and 2 respectively.
- Portfolio validation builds and isolated-installs all six products, then uses
  installed WheelFact to check the real ResidueCheck wheel.

## Completed today (2026-09-20)

- Passed the clean warning-strict 124-test, five-wheel portfolio baseline with
  one expected optional skip and every installed contract.
- Built the frozen ResidueCheck wheel in a disposable copy and recorded its four
  scalar metadata facts, console entry point, and four package modules.
- Implemented WheelFact v0.1.0 with strict schema-v1 parsing, exact comparisons,
  bounded archive reads, deterministic diagnostics, and Python 3.10 fallback.
- Added five tests covering a full pass, every mismatch category, unsafe and
  ambiguous wheels, strict contract errors, and multiline fallback parsing.
- Integrated the new product and its ResidueCheck contract into portfolio
  validation without changing any frozen product behavior.

## Changes since the prior run

The five-product frozen portfolio gained one retained prototype and one installed
artifact gate. ResidueCheck remains unchanged; its built wheel is now checked
before ReleaseFact and WheelContract validations continue.

## Known issues

- WheelFact checks exact declarations, not packaging quality or metadata policy.
- Package payloads are named but never decompressed or content-hashed.
- Standard `.dist-info` generated members are deliberately excluded from exact
  enumeration; scalar metadata and console scripts are checked separately.
- Schema v1 requires at least one payload member and four scalar metadata values.
- The prototype has one real artifact rehearsal; promotion depends on a second.
- Hosted portfolio CI remains Ubuntu-only, and the repository has no Git remote.

## Decisions

- Retain WheelFact v0.1.0: the 16-line real contract is clearer than repeating
  bounded archive parsing and all-mismatch comparison in every release audit.
- Keep WheelFact separate from WheelContract: one checks uninstalled structure,
  while the other owns isolated installed behavior.
- Keep expectations exact and explicit; do not infer, glob, build, install,
  repair, download, or impose general packaging policy.
- Keep all five frozen MVP behaviors unchanged.

## Validation

- The pre-change default `python3` correctly failed the documented build-backend
  preflight; explicit `PYTHON_BIN=python3.11` warning-strict validation passed.
- WheelFact's five focused tests and compilation pass on Python 3.11.
- A freshly built real ResidueCheck wheel passes all nine declared WheelFact
  facts; the focused mismatch fixture reports eight mismatches in one run.
- Final portfolio and compatibility validation is recorded in `DAILY_LOG.md`.

## Recommended next steps

1. Run the second-artifact diagnostic rehearsal in `NEXT_RUN.md`.
2. Freeze WheelFact only if a copied schema-v1 contract is sufficient and every
   deliberate correction is obvious from one report.
3. Do not reopen a frozen product without a demonstrated defect.

No human input is required.

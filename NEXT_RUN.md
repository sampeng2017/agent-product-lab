# Next run: exact wheel-structure experiment

ResidueCheck v1.0.0 is now frozen as the fifth local MVP. ProofRun v1.8.1,
AgentScope v1.0.0, WheelContract v1.0.0, and ReleaseFact v1.0.0 remain frozen.
ReleaseFact v1.0.0 is now frozen as the fourth local MVP.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, and the portfolio validator.
Check Git status/history and rerun warning-strict portfolio validation before
editing.

## Completed experiment

Installed ResidueCheck wrapped a real wheel build from a clean tracked source
copy. It reported ten fresh build artifacts and, after one source edit, only the
two modified outputs. The measured wrapper delta was about 0.09 seconds; a no-op
two-snapshot scan took about 0.10 seconds over 38 entries and 49,167 bytes.

The exercise exposed one diagnostic gap: changed runs did not show their scan
scope. Version 1.0.0 now reports before/after entries and bytes on every completed
check. Its package, installed surfaces, exits, compatibility, and limits passed
release audit, so the product is frozen.

## Bounded next experiment

1. Build the frozen ResidueCheck wheel in a disposable source copy and write the
   smallest explicit contract for distribution name/version, Python requirement,
   license, console entry point, and exact package members.
2. Prototype a dependency-free read-only checker using `zipfile` and standard
   metadata parsing. Keep paths and output deterministic and separate mismatch
   exit 1 from invalid artifact/contract exit 2.
3. Compare the manifest, implementation, and all-mismatch diagnostics with a
   focused standard-library assertion script.
4. Retain a sixth product only if the explicit reusable contract is materially
   clearer than that script and does not overlap installed behavior checks.

## Guardrails

- Do not build or install wheels inside the checker; WheelContract owns installed
  behavior and the portfolio validator owns artifact creation.
- Do not become a general packaging linter, archive repair tool, PyPI client, or
  replacement for established packaging hygiene tools.
- Start with one exact wheel and one strict contract; reject globs or inference
  unless the comparison demonstrates a concrete need.
- Keep all five completed product behaviors frozen unless validation reveals a
  concrete defect.

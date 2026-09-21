# Next run: WheelFact second-artifact rehearsal

WheelFact v0.1.0 is a retained bounded prototype. ResidueCheck v1.0.0,
ReleaseFact v1.0.0, WheelContract v1.0.0, AgentScope v1.0.0, and ProofRun v1.8.1
remain frozen.
ReleaseFact v1.0.0 is now frozen as the fourth local MVP.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, WheelFact's implementation,
tests, documentation, and the portfolio validator. Check Git status/history and
rerun warning-strict portfolio validation before editing.

## Completed experiment

WheelFact checks one existing wheel against exact distribution name, version,
Python requirement, license, console scripts, and non-`.dist-info` payload
members. The real ResidueCheck wheel produces nine passing facts without being
installed. Five focused tests cover a clean artifact, all mismatch categories,
invalid/ambiguous archives, strict contracts, and the Python 3.10 TOML fallback.

The prototype is retained because its short declaration separates artifact
expectations from bounded archive inspection, metadata and entry-point parsing,
set comparison, all-mismatch reporting, and exit semantics. It does not overlap
WheelContract, which owns installed behavior.

## Bounded next rehearsal

1. Build a second frozen portfolio artifact in a disposable source copy and
   write its exact WheelFact contract without changing schema v1.
2. In a disposable contract, deliberately make the distribution/version,
   Python/license, console-script, missing-member, and unexpected-member facts
   stale. Confirm one run makes every correction obvious.
3. Compare the real diagnostic with a focused standard-library assertion script.
4. Promote and freeze only if the second-artifact exercise needs no new schema;
   otherwise make only the smallest demonstrated correction or abandon it.

## Guardrails

- Never build or install inside WheelFact.
- Do not infer expectations from filenames or source trees.
- Do not add globs, repair, PyPI access, general metadata policy, or installed-
  command checks.
- Keep the five completed product behaviors frozen unless validation reveals a
  concrete defect.

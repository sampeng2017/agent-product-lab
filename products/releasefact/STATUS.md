# ReleaseFact status

## Product shape

ReleaseFact v0.1.0 is an active bounded prototype.

It reads one canonical string from a dotted key in TOML, evaluates named exact
one-line `{version}` templates in explicit files, and reports every actual value
that differs. It is dependency-free, deterministic, and read-only.

## Completed on 2026-09-16

- Built the strict schema-v1 contract, core checker, and CLI with exits 0/1/2
  for success, drift, and invalid setup.
- Added exact selector cardinality, path-containment, unknown-field, and
  canonical-value validation.
- Added a three-drift fixture modeled on the stale WheelContract portfolio claim
  and five focused test methods, including the Python 3.10 fallback.
- Added a three-claim product contract plus a seven-claim root portfolio contract
  and integrated source, wheel, install, and real-repository contract validation
  into the portfolio validator.

## Current decision

Retain the prototype. Compared with focused `rg` and shell, the manifest adds a
small amount of declaration but provides reusable all-mismatch extraction,
actual/expected diagnostics, stable ordering, exact selector validation, and
separate drift/setup exits. This clears the experiment's stated threshold.

## Known limits

- Claim templates match complete individual lines and must select exactly one.
- Values are compared as strings; semantic-version precedence is irrelevant.
- Only explicit current-version claims are in scope. Historical mentions must
  not be declared.
- The Python 3.10 fallback reads a basic quoted canonical string rather than
  fully parsing unrelated TOML structures.

## Recommended next step

Deliberately bump ReleaseFact in a disposable checkout to assess how clearly the
seven-claim root contract guides a coordinated release. Add behavior only for a
demonstrated diagnosis gap; otherwise keep the v0.1 surface narrow.

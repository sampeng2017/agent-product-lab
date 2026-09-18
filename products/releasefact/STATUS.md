# ReleaseFact status

## Product shape

ReleaseFact v1.0.0 is a frozen local MVP.

It reads one canonical string from a dotted key in TOML, evaluates named exact
one-line `{version}` templates in explicit files, and reports every actual value
that differs. It is dependency-free, deterministic, and read-only.

## Completed on 2026-09-17

- Rehearsed a 0.1.0 to 0.2.0 release in a disposable repository copy. Changing
  only the canonical value produced all seven expected drifts with exact files,
  lines, actual values, and the expected value.
- Followed the report to a clean pass; the checker caught one documentation
  claim omitted from the first update attempt. No diagnostic was ambiguous,
  redundant, or missing, so schema v1 and behavior remain unchanged.
- Audited wheel contents and metadata, source and installed invocation,
  help/version, passing, drift, and setup exits, docs, tests, and the Python 3.10
  fallback. No product blocker remained.
- Promoted the package from v0.1.0 to v1.0.0 and froze the CLI, schema v1,
  deterministic output, and exit codes 0/1/2.

## Maintenance boundary

Reopen behavior only for a reproduced correctness, safety, compatibility, or
packaging defect. Keep the deliberate limits: explicit complete-line claims,
one canonical TOML string, string equality, no historical inference, and no
write mode.

## Known limits

- Claim templates match complete individual lines and must select exactly one.
- Values are compared as strings; semantic-version precedence is irrelevant.
- Only explicit current-version claims are in scope. Historical mentions must
  not be declared.
- The Python 3.10 fallback reads a basic quoted canonical string rather than
  fully parsing unrelated TOML structures.

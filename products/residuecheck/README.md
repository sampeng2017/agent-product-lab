# ResidueCheck 1.0.0

ResidueCheck is a dependency-free CLI that reports filesystem residue left by
one command, including files ignored by Git. It snapshots a bounded tree before
and after the command and names created, modified, and removed paths.

```bash
residuecheck --root . --exclude .venv --exclude node_modules -- python -m build
```

A clean, successful command exits 0. A failed command or any detected change
exits 1. Invalid input, an unavailable command, or a scan that exceeds a bound
exits 2. Every completed check reports entry and hashed-byte scope for both
snapshots. Command output remains live; ResidueCheck bounds only its own report.

## Safety and scope

- `.git` is always excluded. Additional `--exclude PATH` values are literal
  contained path prefixes, not surprising glob patterns.
- Defaults cap traversal at 10,000 entries, each regular file at 16 MiB, total
  hashed content per snapshot at 256 MiB, and displayed changes at 100.
- Directory symlinks are fingerprinted as links and never followed.
- File contents are streamed into SHA-256 fingerprints and never retained.
- The preflight snapshot completes before the command starts. A post-command
  bound failure is reported as an inspection error; the command's own changes
  are not rolled back.

Tune bounds explicitly with `--max-entries`, `--max-file-bytes`,
`--max-total-bytes`, and `--max-changes`. Use exclusions for dependency,
environment, cache, or output trees that are intentionally outside the check.

## Development

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m residuecheck --help
```

Version 1.0.0 is the frozen local MVP. Its command, output, bounds, exclusions,
and exit 0/1/2 behavior are stable. It is deliberately not a sandbox, watcher,
Git-status replacement, general task runner, or rollback mechanism.

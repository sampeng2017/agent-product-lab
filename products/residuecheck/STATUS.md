# ResidueCheck status

## Product shape

ResidueCheck v1.0.0 is a frozen local MVP. It snapshots one explicitly bounded
directory before and after one command, then reports created, modified, and
removed regular files and symlinks, including Git-ignored paths.

## Release evidence

- An installed-artifact dogfood wrapped a real PEP 517 ReleaseFact wheel build
  from a clean Git archive. It named all ten generated `build/`, `dist/`, and
  `*.egg-info/` files without exclusions.
- After one source edit, the repeated build reported only the copied module and
  rebuilt wheel as modified.
- The fresh direct build took about 0.59 seconds and the wrapped build about
  0.68 seconds on this host. A no-op two-snapshot scan took about 0.10 seconds
  over 38 entries and 49,167 bytes.
- Real dogfood showed that changed runs hid their scan scope. The v1.0.0 output
  now reports before/after entry and byte totals for every completed check and
  uses singular change/entry labels correctly.
- The release audit verified the intended wheel members and metadata, installed
  help/version, exits 0/1/2, Python 3.10 grammar compatibility, warning-strict
  Python 3.11 tests, and focused Python 3.14 tests.

## Stable contract

- One command runs in the inspected root; successful clean checks exit 0,
  command failures or residue exit 1, and setup/inspection failures exit 2.
- Exclusions are literal contained path prefixes and `.git` is always excluded.
- Entry, per-file byte, total byte, and displayed-change bounds remain explicit.
- Reports deterministically order created, modified, and removed paths and name
  the scope of both snapshots.

## Known limits

- It observes only boundary state; transient changes restored before exit are
  invisible.
- It does not restore changes or isolate the command.
- Special filesystem entries and scan races are rejected rather than guessed.
- Command output is inherited and not bounded; only the ResidueCheck report is.
- A post-command scan error cannot enumerate residue beyond the violated bound,
  and the command's changes remain present.
- Exact whole-tree hashing runs twice; the measured cost is intentionally
  controlled by caller-selected bounds and exclusions.

## Decision

Freeze v1.0.0. The real build stayed within the original narrow product shape,
required no glob/configuration expansion, produced useful fresh and repeated
diagnostics, and showed acceptable bounded overhead. Reopen only for a concrete
correctness or safety defect.

# ResidueCheck status

## Product shape

ResidueCheck v0.1.0 is an active bounded prototype. It snapshots one explicitly
bounded directory before and after one command, then reports created, modified,
and removed regular files and symlinks, including Git-ignored paths.

## Initial evidence

The ReleaseFact audit showed that direct wheel builds refreshed ignored
`*.egg-info/` data while Git status stayed clean. A disposable ignored-file
fixture reproduces all three change kinds. ResidueCheck expresses the guard in
one invocation and supplies deterministic aggregation, exclusions, traversal
and byte bounds, symlink safety, and report truncation that focused portable
`find` plus hashing shell must reimplement.

## Known limits

- It observes only boundary state; transient changes restored before exit are
  invisible.
- It does not restore changes or isolate the command.
- Special filesystem entries and scan races are rejected rather than guessed.
- Command output is inherited and not bounded; only the ResidueCheck report is.
- A post-command scan error cannot enumerate the residue beyond the violated
  bound, and the command's changes remain present.

## Next decision

Dogfood the installed prototype around a real build in a disposable source
copy. Retain it only if the report catches realistic residue without cumbersome
exclusions or unacceptable hashing cost.

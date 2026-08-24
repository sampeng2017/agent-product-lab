# AgentScope status

## Product shape

AgentScope v0.4.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence; its `copilot-cli` profile combines supported
ancestor formats, evaluates one-line `applyTo` globs, and recursively resolves
supported `@` imports. Human and versioned JSON output are available, with
optional missing-instructions, invalid-reference, and profile-divergence gates.

## Completed on 2026-08-23

- Added `--fail-on-invalid-references` to inspection. It exits 1 after rendering
  the full report when any target has a rejected Copilot reference edge, while
  informational inspection still exits 0 and invalid repository input exits 2.
- Defined gate composition explicitly: invalid-reference and
  `--require-instructions` policies use OR semantics across every target.
- Added aggregate and per-target invalid-reference counts to human output and
  inspection JSON without hiding the ordered source-level diagnostic reasons.
- Versioned inspection JSON from schema v1 to v2 for the two additive
  `invalid_reference_count` fields. Comparison JSON remains schema v1.
- Expanded the suite from 20 to 21 tests with default, independent, combined,
  multi-target, JSON, human, and invalid-input exit-contract coverage.

## Known issues

- The Copilot profile models repository inputs only, not user-level instruction
  directories or configuration.
- Path-specific frontmatter supports only a scalar, comma-separated `applyTo`;
  unsupported or malformed forms are currently collapsed into an ignored
  source instead of receiving a precise diagnostic.
- `excludeAgent`, YAML lists, and syntax errors are not analyzed.
- AgentScope does not reproduce Copilot CLI's unpublished import size guard;
  the local 10-edge depth limit is intentionally product-defined.
- GitHub's Copilot CLI documentation does not explicitly demonstrate `?`;
  AgentScope documents its conventional single-character behavior as a product
  contract rather than claiming universal Copilot compatibility.

## Decisions

- Stay read-only and dependency-free for the first useful experience.
- Use named client profiles rather than a misleading universal scope model.
- Allow nonexistent targets so maintainers can inspect guidance before creating
  a planned file; resolved paths still cannot escape the selected repository.
- Define divergence strictly from applied source paths: ignored and invalid
  sources do not differ in effective guidance and do not fail comparison.
- Treat a leading dot as a real path character; remove only one exact `./`
  relative marker and do not reinterpret a leading `/`.
- Resolve symlinks before enforcing repository containment, and do not expand
  imports from source formats GitHub excludes.
- Count invalid-reference diagnostic occurrences per target, because one shared
  source can affect several requested targets and each assessment is actionable.
- Keep policy opt-in and orthogonal: either requested inspection gate can fail
  the command, while usage failures keep their distinct exit 2 contract.
- Version only inspection JSON for the additive diagnostic counts; keep the
  unchanged comparison document on schema v1.

## Recommended next step

Classify malformed path-instruction frontmatter as explicit diagnostics,
including unsupported list values and malformed delimiters, then decide whether
to generalize the invalid-reference policy into a broader invalid-source gate.

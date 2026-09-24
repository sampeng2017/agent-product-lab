# GrammarCheck 0.1.0

> **Archived experiment.** A 2026-09-23 diagnostic rehearsal found that a
> 13-line direct `ast.parse`/`compile` loop reported the same incompatible
> files, while Ruff 0.16.8 produced richer contextual diagnostics. This
> prototype is kept as decision evidence but is not an active portfolio product.

GrammarCheck is a dependency-free, read-only CLI that checks Python source
files against an explicit older Python grammar without requiring that older
interpreter locally.

```bash
grammarcheck --root . --target 3.10 src tests
```

It recursively selects `.py` files under explicit contained paths, parses each
with CPython's `ast.parse(feature_version=...)`, then compiles the resulting AST
to catch scope errors that parsing alone permits. Compatible, incompatible, and
invalid inspections exit 0, 1, and 2 respectively. Reports are deterministic
and include every incompatible file plus the inspected file and byte totals.

The source set is bounded by default to 10,000 files, 1 MiB per file, and 50
MiB total. Symlink sources and paths outside `--root` are rejected. Bounds can
be raised explicitly.

## Boundary

GrammarCheck is a grammar preflight, not an interpreter emulator. CPython
documents `feature_version` as a best-effort grammar parse. A passing result
does not prove runtime semantics, standard-library availability, dependency
compatibility, type correctness, or success on the target interpreter. A real
minimum-version test job remains the authoritative compatibility check.

Ruff offers broader target-version-aware linting and formatting and should be
preferred when a project already uses it. GrammarCheck's wedge is the narrow,
dependency-free question: “do these files parse and compile under this explicit
grammar?”

## Experiment result

Against separate Python 3.11 exception-group, 3.12 type-alias, 3.13 type-
parameter-default, compiler-scope, and compatible fixtures, GrammarCheck found
all four incompatible files and reported one passing file. The direct AST loop
found the same four incompatibilities. Ruff additionally emitted source excerpts
and both the 3.12 type-statement and 3.13 default-type-parameter errors for the
same 3.13 fixture. The bounds and aggregate were useful, but did not justify a
seventh maintained CLI.

## Development

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m grammarcheck --root ../.. --target 3.10 products/grammarcheck/src products/grammarcheck/tests
```

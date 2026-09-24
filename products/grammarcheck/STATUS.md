# GrammarCheck status

## Product shape

GrammarCheck v0.1.0 is an archived bounded experiment for checking explicit
source paths against an older CPython grammar without installing that
interpreter. It was not promoted to a maintained local MVP.

## Initial evidence

- All six portfolio products declare Python 3.10+, while routine local
  validation uses Python 3.11 and prior “3.10 grammar” checks were ad hoc.
- CPython exposes target grammar parsing but explicitly notes that parsing alone
  misses compiler scope checks; GrammarCheck performs both stages.
- One installed command can check every product's source and tests with stable
  paths, complete diagnostics, symlink rejection, and file/byte bounds.

## Decision result

- This is not runtime, API, dependency, type, lint, format, or exact-interpreter
  compatibility evidence.
- The 2026-09-23 rehearsal covered Python 3.11, 3.12, and 3.13 syntax plus a
  compiler-only error and found every deliberately incompatible file.
- A 13-line direct AST/compile loop found the same incompatibilities; Ruff
  0.16.8 produced richer contextual and multi-error output.
- The product is archived and excluded from active portfolio validation. Its
  source and tests remain as reproducible decision evidence.

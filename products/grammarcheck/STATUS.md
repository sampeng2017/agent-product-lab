# GrammarCheck status

## Product shape

GrammarCheck v0.1.0 is a bounded prototype for checking explicit source paths
against an older CPython grammar without installing that interpreter.

## Initial evidence

- All six portfolio products declare Python 3.10+, while routine local
  validation uses Python 3.11 and prior “3.10 grammar” checks were ad hoc.
- CPython exposes target grammar parsing but explicitly notes that parsing alone
  misses compiler scope checks; GrammarCheck performs both stages.
- One installed command can check every product's source and tests with stable
  paths, complete diagnostics, symlink rejection, and file/byte bounds.

## Boundaries and decision test

- This is not runtime, API, dependency, type, lint, format, or exact-interpreter
  compatibility evidence.
- The next run should deliberately introduce several post-3.10 syntax forms in
  a disposable portfolio copy and compare the report with Ruff and direct
  interpreter checks.
- Retain only if the aggregate bounded report remains clearer than a small AST
  script for this repository; otherwise archive the experiment.

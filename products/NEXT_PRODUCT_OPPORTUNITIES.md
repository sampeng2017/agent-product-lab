# Next-product opportunity comparison — 2026-09-11

This comparison follows AgentScope's v1.0.0 release audit. It favors a frequent,
specific local workflow that can produce a useful credential-free prototype.

## Candidate 1: installed-artifact behavior contract runner — selected

- **Target user:** maintainers of Python command-line packages who test source
  thoroughly but only perform a shallow smoke after building a wheel.
- **Painful job:** prove that the artifact users install exposes every intended
  command, emits parseable output, and retains documented exit contracts.
- **Concrete evidence:** before this audit, portfolio CI built and isolated-
  installed AgentScope but exercised only `agentscope --version`. A broken
  packaged inspection, comparison, coverage, JSON, or policy path could pass.
- **Smallest useful wedge:** a dependency-free TOML contract runner that builds
  or accepts one wheel, installs it in a disposable environment, runs explicit
  argument vectors, and checks exit codes plus small stdout/JSON assertions.
- **Alternatives:** tox can build/install wheels and run arbitrary environment
  commands, but it is a broad multi-environment orchestrator. Bespoke shell is
  lightweight but repeats fragile exit and JSON checks between projects.
- **Principal risk:** the wedge is too small unless its manifest and diagnostics
  are substantially clearer than a short CI function.

## Candidate 2: wheel-content auditor

- **Painful job:** catch missing package files, accidental tests or caches, and
  malformed top-level layouts before upload.
- **Why not selected:** `check-wheel-contents` already checks common wheel file-
  tree mistakes and can compare a source package tree with wheel paths. A new
  local MVP would have little differentiated surface.

## Candidate 3: package metadata and README release checker

- **Painful job:** catch metadata defects and broken long-description rendering
  before publishing to PyPI.
- **Why not selected:** the Python Packaging User Guide already recommends
  `twine check` for built distributions. Extending that surface would require a
  narrower unmet case than this portfolio has demonstrated.

## Candidate 4: general Python environment matrix runner

- **Painful job:** build, install, and test packages across interpreter and
  dependency combinations.
- **Why not selected:** tox already owns this broader job with isolated build and
  run environments, wheel/sdist modes, and structured configuration. Competing
  at that scope would sacrifice the portfolio's small-product constraint.

## Decision and first evidence

Select the installed-artifact behavior contract runner. The enhanced portfolio
validator is its first dogfood specimen: it now exercises AgentScope's three
installed human surfaces and three JSON policy-failure paths, checks exact exit
1 semantics, and validates schema versions and key aggregates. The next run
should extract only this proven pattern into a standalone prototype and compare
its manifest/diagnostics against the equivalent shell before committing to the
product.

## Sources inspected

- [Python Packaging User Guide: package formats](https://packaging.python.org/en/latest/discussions/package-formats/)
  — wheels are install artifacts whose contents can be inspected directly.
- [Python Packaging User Guide: PyPI-friendly README](https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/)
  — recommends `twine check` for distribution rendering validation.
- [check-wheel-contents](https://github.com/jwodder/check-wheel-contents) —
  established wheel file-tree and packaging-error checks.
- [tox packaging concepts](https://tox.wiki/en/4.40.0/explanation.html) —
  established isolated build/install and environment command orchestration.

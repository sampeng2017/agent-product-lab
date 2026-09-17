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

## Prototype result — 2026-09-12

WheelContract v0.1.0 validates the hypothesis strongly enough to continue. Its
strict 52-line contract expresses six AgentScope human, JSON, and policy-exit
cases while the portfolio validator sheds 67 lines of bespoke shell and embedded
Python parsing. The same installed runner produces ordered per-case results and
aggregated failures, applies time and output bounds, removes checkout import
variables, and can consume the already-built wheel.

This is a clarity and reuse improvement even though the contract itself is not
shorter than the command list alone: expectations are adjacent to each case,
failure semantics are shared and tested, and the CI shell no longer implements
a one-off assertion framework. Continue WheelContract narrowly, using real
contract diagnostics as the evidence for the next feature rather than expanding
into general environment orchestration.

## Next-product comparison — 2026-09-15

WheelContract's v1.0.0 audit supplied fresh repository-local evidence for the
next choice. The comparison favors a bounded, credential-free experiment over
reopening any frozen product.

### Candidate 1: release-fact consistency checker — selected

- **Demonstrated pain:** `products/README.md` still called WheelContract an
  active v0.1.0 prototype after the implementation, package metadata, contract,
  root README, and status had advanced to v0.3.0.
- **Smallest useful wedge:** read one canonical version from project TOML and
  verify explicit current-version claims in a short allowlist of source,
  contract, and documentation files; report all drift without editing.
- **Decision test:** retain it only if its declaration and complete diagnostics
  are materially clearer than focused `rg` plus shell comparisons.
- **Principal risk:** configurable text matching becomes a generic regex engine
  or adds more maintenance than the drift it prevents.

### Candidate 2: documentation command-example executor

- **Evidence:** all three products expose multiple README commands, but their
  focused suites and installed behavior contracts already cover the important
  surfaces.
- **Why not selected:** reliable example execution would need per-snippet setup,
  fixtures, and skip semantics, quickly overlapping WheelContract and general
  documentation-test tools.

### Candidate 3: cross-platform process-cleanup probe

- **Evidence:** WheelContract's Windows process-tree path is unit-pinned but not
  live-tested, while macOS is live-tested and Ubuntu CI is configured.
- **Why not selected:** the missing evidence requires a Windows runner or remote
  CI rather than a distinct local product; the repository currently has neither.

### Candidate 4: temporary-output disk limiter

- **Evidence:** WheelContract bounds reads and diagnostics but spools child
  output to temporary files before reading.
- **Why not selected:** no real contract has demonstrated problematic disk use,
  and a robust cross-platform streaming limiter would reopen a frozen product
  for speculative complexity.

### Selected experiment

Prototype `ReleaseFact` against a disposable fixture modeled on today's stale
portfolio claim. Keep the first slice read-only: one canonical TOML value,
explicit file claims, deterministic all-mismatch output, and separate drift
versus invalid-setup exits. Do not dogfood or retain it until comparison with the
equivalent shell demonstrates a clarity or diagnostic advantage.

## Prototype result — 2026-09-16

ReleaseFact v0.1.0 meets the retention threshold. Its schema-v1 contract names
one canonical TOML string and exact one-line templates with a single version
slot. A fixture modeled on the stale WheelContract portfolio claim reports three
different actual versions, expected value, file, and line in one deterministic
run. Missing or ambiguous selectors are setup exit 2 rather than misleading
drift exit 1.

The declaration is slightly longer than three focused searches. The equivalent
reliable shell, however, must also extract values, continue after failures,
validate selector cardinality, preserve order, distinguish invalid setup, and
aggregate the result. Centralizing that tested behavior is a material clarity
and reuse gain. A seven-claim root contract now dogfoods package, product docs,
and portfolio docs from the installed wheel.

Retain the product narrowly. The next run should rehearse a version bump in a
disposable checkout and change schema v1 only if that exercise demonstrates a
specific diagnosis gap.

## Sources inspected for the 2026-09-11 comparison

- [Python Packaging User Guide: package formats](https://packaging.python.org/en/latest/discussions/package-formats/)
  — wheels are install artifacts whose contents can be inspected directly.
- [Python Packaging User Guide: PyPI-friendly README](https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/)
  — recommends `twine check` for distribution rendering validation.
- [check-wheel-contents](https://github.com/jwodder/check-wheel-contents) —
  established wheel file-tree and packaging-error checks.
- [tox packaging concepts](https://tox.wiki/en/4.40.0/explanation.html) —
  established isolated build/install and environment command orchestration.

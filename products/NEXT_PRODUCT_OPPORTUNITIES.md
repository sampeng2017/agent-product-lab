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

## ReleaseFact release result — 2026-09-17

The disposable seven-claim rehearsal changed only the canonical version first.
ReleaseFact named all seven stale files and lines with their actual and expected
values. After the first claim update pass, it caught one root README claim that
had been missed; following that final diagnostic produced a clean run. No output
was ambiguous or redundant, and no claim was missing.

A release audit then verified the wheel contents and metadata, installed and
source command surfaces, help/version, passing contract, aggregate drift exit 1,
invalid-setup exit 2, docs, tests, and the Python 3.10 fallback. ReleaseFact was
promoted unchanged from v0.1.0 to v1.0.0 and frozen as the fourth local MVP.

## Next-product comparison — 2026-09-17

The release audit also exposed new repository-local evidence: the portfolio
validator claimed to leave the checkout unchanged, but direct PEP 517 builds
refreshed ignored `*.egg-info/` directories. Ordinary Git status remained clean.
The validator now builds from temporary source copies, but the detection gap is
worth one bounded experiment.

### Candidate 1: ignored command-residue detector — selected experiment

- **Demonstrated pain:** build metadata changed in every product checkout while
  the validator and Git status both appeared clean.
- **Smallest useful wedge:** compare a bounded filesystem snapshot before and
  after one command and report created, modified, and removed paths, including
  ignored files, without retaining file contents or changing the target tree.
- **Decision test:** retain it only if exclusions, bounds, and the resulting
  report are materially clearer than focused `find` plus hashing shell.
- **Principal risk:** it becomes a general runner or performs expensive,
  surprising traversal over dependencies and caches.

### Candidate 2: wheel metadata contract

- **Evidence:** today's release audit manually inspected name, version, license,
  Python requirement, entry point, and wheel members.
- **Why not selected:** the portfolio already validates installed behavior, and
  established packaging checks cover common metadata/content failures. The
  ignored-residue defect is both fresher and not covered by current gates.

### Candidate 3: documentation command executor

- **Evidence:** all four products document local commands that are partly
  repeated in validation.
- **Why not selected:** fixture/setup semantics would overlap WheelContract and
  broader documentation-test tooling without a newly demonstrated failure.

### Candidate 4: local Python-version matrix runner

- **Evidence:** hosted CI declares Python 3.10 through 3.14 while local runs
  usually exercise one or two installed interpreters.
- **Why not selected:** interpreter availability is environmental, the existing
  CI matrix already owns the contract, and no matrix-only defect was observed.

## Ignored-residue prototype result — 2026-09-18

ResidueCheck v0.1.0 meets the initial retention threshold. A disposable fixture
with `*.cache` ignored reproduces created, modified, and removed command output;
the tool names all three even though an equivalent Git status is empty.

The compact invocation is materially clearer than the focused portable shell
alternative. Reliable shell needs two sorted path manifests, explicit pruning,
per-file size checks and hashing, total limits, a three-way join/diff, bounded
rendering, cleanup, and careful failure propagation around the wrapped command.
ResidueCheck centralizes those mechanics while keeping exclusions literal and
visible. Its cost is also explicit: it traverses twice and hashes every included
regular byte twice, bounded by entry, per-file, and total-byte limits.

Retain the prototype narrowly. The next decision should wrap an actual wheel
build in a disposable product copy, measure the scan, and inspect whether normal
build exclusions become cumbersome. Do not add configuration, rollback,
watching, or sandbox behavior unless that exercise proves a concrete need.

## ResidueCheck release result — 2026-09-19

The installed v0.1.0 artifact wrapped a real ReleaseFact PEP 517 wheel build from
a clean Git archive. It reported all ten created `build/`, `dist/`, and
`*.egg-info/` files. After one source edit, a repeated build reported only the
copied module and rebuilt wheel as modified. No glob exclusions were needed.

The direct fresh build took about 0.59 seconds and the wrapped build about 0.68
seconds on this host. A no-op two-snapshot scan took about 0.10 seconds over 38
entries and 49,167 bytes. The dogfood did expose one diagnostic gap: changed
runs did not disclose that scope. Version 1.0.0 now reports before/after entry
and byte totals on every completed check and correctly renders singular counts.

Wheel contents/metadata, installed help/version, exits 0/1/2, Python 3.10 grammar
compatibility, and Python 3.11/3.14 behavior passed audit. ResidueCheck is frozen
as the fifth local MVP without adding configuration, globs, rollback, or watcher
behavior.

## Next-product comparison — 2026-09-19

ResidueCheck's release audit repeated a manual pattern already used for the
other artifacts: inspect exact wheel members, metadata, and entry points before
freezing. That provides the strongest repository-local candidate for one more
bounded experiment.

### Candidate 1: exact wheel-structure contract — selected experiment

- **Demonstrated pain:** every release audit uses a bespoke `zipfile`/metadata
  snippet to confirm name, version, Python requirement, license, entry point,
  and intended package members.
- **Smallest useful wedge:** check one existing wheel against one strict TOML
  contract with exact scalar metadata, console entry points, and package member
  lists; report every mismatch without building or installing anything.
- **Decision test:** retain it only if the declaration and complete diagnostics
  are materially clearer than a focused standard-library assertion script.
- **Principal risk:** it grows into a general packaging linter already served by
  established ecosystem tools or overlaps WheelContract's installed behavior.

### Candidate 2: portfolio interpreter selector

- **Evidence:** the default `python3` lacked the required build backend while
  local `python3.11` satisfied it, so today's first validation preflight failed.
- **Why not selected:** `PYTHON_BIN` already makes selection explicit, and silent
  interpreter discovery would weaken reproducibility for a local convenience.

### Candidate 3: ignored build-artifact cleanup

- **Evidence:** historical `build/` and `*.egg-info/` trees remain in product
  directories even though current validation uses temporary source copies.
- **Why not selected:** cleanup is destructive, ownership predates current runs,
  and residue detection—not deletion—is the reusable behavior demonstrated.

### Candidate 4: persistent ResidueCheck benchmark reports

- **Evidence:** the release dogfood measured traversal size and elapsed overhead.
- **Why not selected:** the stable CLI now exposes scan scope, while timing is
  host- and command-specific and does not justify a report schema.

The next run should prototype the exact wheel-structure contract against the
frozen ResidueCheck wheel. Abandon it if a short transparent script remains the
clearer maintenance choice.

## GrammarCheck experiment result — 2026-09-23

GrammarCheck v0.1.0 did not clear its retention threshold. A disposable fixture
combined one compatible file with Python 3.11 exception-group syntax, a Python
3.12 type statement, a Python 3.13 default type parameter, and a compiler-only
top-level `return`. Targeting Python 3.10, GrammarCheck reported all four
incompatible files, their locations and reasons, one pass, and bounded totals.

A focused 13-line `ast.parse(feature_version=(3, 10))` plus `compile` loop
reported the same four incompatible files and reasons. Current Ruff 0.16.8 also
reported all four, added source excerpts, and emitted both the type-statement
and default-type-parameter incompatibilities for the Python 3.13 file. Its
documented `target-version` setting already covers this broader maintained use
case.

The stable path selection and bounds were useful but did not outweigh a seventh
package's maintenance and build cost. Keep the prototype as archived evidence,
remove it from active portfolio validation, and select a different opportunity
next run rather than expanding its scope.

## Source-distribution rehearsal result — 2026-09-25

A disposable ReleaseFact build used the standard `build` frontend to create an
sdist and direct wheel, then pip built and installed a wheel from that sdist.
The two wheels were byte-identical, both published artifacts passed
`twine check --strict`, and installed behavior passed. This did not demonstrate
evidence beyond the existing direct-wheel, WheelFact, and WheelContract gates,
so a permanent sdist dependency and validation path were rejected.

Two sdists built from separate source copies were not byte-identical even with
the Git-derived `SOURCE_DATE_EPOCH`: both source and generated tar member mtimes
reflected their copy/build times. Because the portfolio publishes no sdists,
normalizing those archives would be speculative rather than a current product
improvement.

The frontend did expose an overdue setuptools warning for every package's
legacy license table. All packages now use SPDX `license` plus `license-files`
metadata and require setuptools 77+. WheelFact v1.0.1 recognizes the resulting
`License-Expression` header while retaining legacy `License` compatibility.
The next bounded opportunity is wheel `RECORD` integrity: deliberately corrupt
hash, size, and membership evidence and determine whether current install,
structure, and behavior checks have a real blind spot before extending a tool.

## Exact wheel-structure prototype result — 2026-09-20

WheelFact v0.1.0 meets the initial retention threshold. Its strict contract for
the real ResidueCheck wheel names four scalar metadata facts, one console entry
point, and the exact four-file payload. The checker reads the existing archive
without building or installing it and reports all missing, unexpected, and
unequal facts deterministically with mismatch exit 1 versus invalid-input exit
2.

A focused standard-library assertion script is shorter for a single fixed
artifact, but each release audit would need to repeat safe archive selection,
bounded metadata reads, email and entry-point parsing, exact set differences,
all-mismatch rendering, and exit semantics. The 16-line TOML declaration keeps
artifact expectations separate from those tested mechanics, so it is clearer
for the portfolio's repeated audits without overlapping WheelContract's
installed behavior.

Retain the prototype narrowly. The next run should copy its contract for a
second frozen wheel, deliberately stale every fact category, and promote or
abandon the schema based on the real diagnostic rehearsal. Do not add builds,
installs, globs, inferred expectations, repair, or general packaging policy.

## WheelFact release result — 2026-09-21

The second artifact used AgentScope's larger frozen wheel. Its exact 16-line
schema-v1 contract passed four scalar facts, one console script, and four
payload members. A deliberately stale copy changed all scalar values, replaced
the console script, omitted one real member, and named one absent member. One
run reported all eight corrections while retaining the three passing member
facts; no diagnostic or schema gap appeared.

The focused standard-library comparison required 44 lines and still omitted
WheelFact's unsafe/duplicate archive rejection, `.dist-info` ambiguity checks,
read bounds, strict contract parsing, and stable setup-error behavior. The
declaration remains the clearer repeated release-audit interface. WheelFact was
promoted unchanged to v1.0.0 and frozen as the sixth local MVP. The next run
should compare fresh opportunities rather than extend exact wheel checks into
general packaging policy.

## Sources inspected for the 2026-09-11 comparison

- [Python Packaging User Guide: package formats](https://packaging.python.org/en/latest/discussions/package-formats/)
  — wheels are install artifacts whose contents can be inspected directly.
- [Python Packaging User Guide: PyPI-friendly README](https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/)
  — recommends `twine check` for distribution rendering validation.
- [check-wheel-contents](https://github.com/jwodder/check-wheel-contents) —
  established wheel file-tree and packaging-error checks.
- [tox packaging concepts](https://tox.wiki/en/4.40.0/explanation.html) —
  established isolated build/install and environment command orchestration.

## Next-product comparison — 2026-09-22

WheelFact's freeze left the portfolio without an active experiment. Fresh
repository inspection found that all six packages declare Python 3.10+, hosted
CI tests that minimum, but local release notes repeatedly cite one-off “Python
3.10 grammar parsing” alongside routine Python 3.11 validation.

### Candidate 1: bounded target-grammar preflight — selected experiment

- **Demonstrated pain:** there was no checked-in command that could detect a
  newly introduced post-3.10 syntax form without running Python 3.10 itself.
- **Smallest useful wedge:** recursively select explicit contained `.py` paths,
  parse them with an explicit CPython `feature_version`, compile the resulting
  AST for scope checks, and report every incompatible file under file/byte
  bounds.
- **Existing ownership:** Ruff already uses `requires-python` or an explicit
  target version for broad lint and format behavior. This repository does not
  otherwise need Ruff; the experiment must remain a narrow dependency-free
  grammar preflight and clearly defer to Ruff where it is already present.
- **Decision test:** retain only if one aggregate portfolio check and its
  bounded diagnostics are clearer than a focused AST script.
- **Principal risk:** CPython documents feature-version parsing as best effort;
  a pass cannot be presented as runtime compatibility evidence.

### Candidate 2: declared-support/CI-matrix consistency checker

- **Evidence:** every package repeats `requires-python = ">=3.10"`, while the
  GitHub workflow separately enumerates 3.10 through 3.14.
- **Why not selected:** `requires-python` is standardized project metadata, but
  interpreting arbitrary specifiers and GitHub matrix expressions would need a
  packaging library plus YAML semantics. The current concrete risk is syntax
  drift, and the hosted matrix remains the authoritative runtime evidence.

### Candidate 3: reproducible wheel comparison

- **Evidence:** portfolio validation builds all six wheels on every run, but it
  does not compare independent builds.
- **Why not selected:** no nondeterministic artifact was observed, and the
  reproducible-builds ecosystem already standardizes `SOURCE_DATE_EPOCH` for
  build tools. A twin-build comparator would be speculative and overlap the
  existing artifact inspection products without a demonstrated failure.

### Prototype result

GrammarCheck v0.1.0 meets the initial retention threshold. One installed command
checks source and tests for all seven products against Python 3.10 grammar,
deduplicates overlapping paths, rejects symlink/escaping inputs, caps count and
bytes, and separates incompatibility exit 1 from invalid inspection exit 2.
Focused tests prove both grammar rejection and the compiler-only “return outside
function” failure. The next run should inject multiple post-3.10 forms in a
disposable copy and compare its complete report with direct AST and Ruff output
before deciding whether to freeze or abandon the product.

## Sources inspected for the 2026-09-22 comparison

- [CPython `ast` documentation](https://docs.python.org/3/library/ast.html) —
  `feature_version` attempts an older grammar parse; parsing alone does not
  perform every compilation/scoping check.
- [Ruff target-version settings](https://docs.astral.sh/ruff/settings/#target-version)
  — Ruff can infer the minimum target from `requires-python` and applies it to
  version-aware lint and format behavior.
- [PyPA `pyproject.toml` specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/#requires-python)
  — `requires-python` is the standard project compatibility declaration.
- [Reproducible Builds `SOURCE_DATE_EPOCH`](https://reproducible-builds.org/docs/source-date-epoch/)
  — the existing cross-ecosystem convention for deterministic build dates.

## Portfolio release-evidence comparison — 2026-09-24

The archived GrammarCheck left no active product hypothesis. Inspection focused
on missing release evidence that could be demonstrated before adding code.

### Candidate 1: reproducible wheel gate — selected

- **Demonstrated pain:** two clean ReleaseFact builds three seconds apart had
  identical members, payload CRCs, and sizes but different wheel SHA-256 values;
  only generated archive timestamps changed.
- **Smallest useful wedge:** set the standardized `SOURCE_DATE_EPOCH` to the
  latest Git commit time, build every product from two independent temporary
  source copies, and require byte equality before installation.
- **Existing ownership:** the Reproducible Builds project defines the variable
  and explicitly documents deriving it from `git log`. A separate comparator
  CLI would add no value over two builds and `cmp` for this portfolio.
- **Decision test:** retain only if the standard variable makes the real wheel
  byte-identical after a delayed rebuild. The hashes matched, so the portfolio
  gate was retained without creating a seventh product.

### Candidate 2: local documentation-link gate

- **Evidence:** release audits repeatedly mention documentation links, but a
  disposable scan found all 24 local Markdown targets present.
- **Why not selected:** there is no current defect, a small local-only parser
  would mishandle Markdown edge cases, and lychee already checks local and
  remote links across common documentation formats.

### Candidate 3: source-distribution release path

- **Evidence:** all six products build, inspect, install, and exercise direct
  wheels, but none builds an sdist or builds a wheel from one. PyPA recommends
  publishing both formats because installers may fall back to an sdist.
- **Why not selected today:** the standard `build` frontend is not installed in
  the local validation environment, and no missing-file or install defect has
  yet been reproduced. This is the strongest bounded next rehearsal, not a
  reason to silently add dependencies or invent an sdist checker.

### Result

The reproducibility hypothesis changed from speculative to demonstrated. The
portfolio validator now creates twelve wheels per interpreter run and compares
each product's independent pair byte for byte before continuing with existing
structure and behavior contracts. A missing or malformed Git commit timestamp
is a setup error rather than an implicit wall-clock fallback. Product APIs and
schemas remain frozen.

## Sources inspected for the 2026-09-24 comparison

- [Reproducible Builds `SOURCE_DATE_EPOCH`](https://reproducible-builds.org/docs/source-date-epoch/)
  — standard timestamp input, including the recommended latest-Git-commit
  derivation and ZIP timestamp handling.
- [PyPA packaging flow](https://packaging.python.org/en/latest/flow/) — standard
  release flow normally produces both an sdist and one or more wheels.
- [PyPA package formats](https://packaging.python.org/en/latest/discussions/package-formats/)
  — installers can fall back to building a wheel from an sdist, and publishers
  should normally provide both.
- [lychee](https://github.com/lycheeverse/lychee) — established link checker for
  Markdown and other documentation formats.

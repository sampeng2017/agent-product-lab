# AgentScope

AgentScope is a local, read-only CLI that explains which coding-agent
instruction files apply to a target path. It makes nested `AGENTS.md` precedence
and multi-format Copilot CLI aggregation visible before an agent edits code.

## Try it

AgentScope requires Python 3.10 or newer and has no runtime dependencies.

```bash
cd products/agentscope
PYTHONPATH=src python3 -m agentscope --root ../.. products/agentscope/src/agentscope/core.py
PYTHONPATH=src python3 -m agentscope --profile copilot-cli --root ../.. --cwd products/agentscope --json products/agentscope/src/agentscope/core.py
PYTHONPATH=src python3 -m agentscope compare --root ../.. --cwd products/agentscope products/agentscope/src/agentscope/core.py
PYTHONPATH=src python3 -m agentscope coverage --root ../.. products/agentscope/src/agentscope/core.py products/agentscope/README.md
PYTHONPATH=src python3 -m agentscope coverage --compact --root ../.. products/agentscope/src/agentscope/core.py products/agentscope/README.md
```

`--cwd` is an explicit Copilot session directory; relative values are anchored
at `--root`, and absolute values are accepted only when contained by it. The
directory must exist, AgentScope never changes its process directory, and the
option defaults to the repository root so existing invocations retain v0.6.0
discovery behavior.

Repeat `--instructions-dir PATH` to model directories that would otherwise be
listed in `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`. AgentScope deliberately does not
read that environment variable: relative paths are anchored at `--root`, each
directory must exist and remain repository-contained after symlink resolution,
and equivalent paths are reported once. Each directory contributes its direct
`AGENTS.md` plus recursively discovered `*.instructions.md` files. Ordinary
repository/session sources are reported first, followed by additional
directories in caller order and their modular files in path order.

Unreadable or non-UTF-8 Copilot sources are reported as `invalid` with stable
diagnostics that do not expose platform exception details. AgentScope does not
content-compare them or expand apparent references from undecodable content.
Use `--require-instructions` to turn missing applicable guidance into exit 1;
use `--fail-on-ignored-sources` to reject a discovered path instruction whose
`applyTo` patterns do not match a requested target without rejecting duplicate
copies or shadowed ancestors;
use `--fail-on-invalid-references` to reject cycles, missing imports, and other
invalid Copilot reference edges. Use the broader `--fail-on-invalid-sources` to
also reject malformed path-instruction frontmatter. Any requested gate exits 1
when its condition occurs for any target, and they compose with OR semantics.
Invalid repository input exits 2. Without a gate, inspection is informational
and exits 0. Multiple target paths can be inspected in one invocation.

Inspection JSON uses schema v5 and comparison JSON uses schema v5. Both record
the effective deduplicated `additional_instruction_directories` list; target
and inspection source objects are unchanged. Comparison v5 retains ordered
non-applied (`ignored`, `duplicate`, and `shadowed`) and invalid source objects
plus their counts per profile, target, and document. Aggregates sum source-state
occurrences per target/profile.

Use `compare` to evaluate every target under both profiles. It reports common
and profile-only applied source paths plus each profile's ordered non-applied
evidence and invalid diagnostics in human or schema-v5 JSON form. A target is
`UNGUIDED` only when no profile applies any source; one-profile coverage is
instead `DIVERGENT`.
Comparison is informational by default. `--require-instructions` exits 1 for an
unguided target while intentionally allowing one-profile coverage;
`--fail-on-divergence` is the separate stricter profile-parity policy.
`--fail-on-ignored-sources` narrowly rejects unmatched path rules, not other
non-applied states such as duplicates or shadowed ancestors.
`--fail-on-invalid-references` narrowly rejects broken import edges, and
`--fail-on-invalid-sources` also rejects other invalid guidance. The gates
compose with OR semantics and render the full report before failing. Invalidity
remains separate from applied-path divergence and guidance coverage.

`coverage` provides the complementary source-oriented view for the
`copilot-cli` profile. It groups only discovered modular
`*.instructions.md` sources and lists their matched, ignored, or invalid
occurrences in caller target order. Each source reports how many requested
targets actually discovered it; a target outside a nested discovery location
is absent rather than incorrectly classified as ignored. Standard instructions,
references, duplicates, and `agents-md` shadows stay outside this focused view.
Coverage JSON has its own schema v1 and includes the ordered requested targets,
aggregate occurrence counts, patterns, and per-source target occurrences.
Use `coverage --compact` for a source-by-target human matrix: `M`, `I`, and `X`
represent matched, ignored, and invalid occurrences, while `-` means the source
was not discovered for that target. Numbered rule and target legends preserve
full paths, patterns, first-discovery order, and caller order; use the default
view when occurrence reasons are needed. `--compact` and `--json` are mutually
exclusive, and compact presentation does not change policy results.
`coverage --fail-on-ignored-sources` and `--fail-on-invalid-sources` retain the
post-render exit-1 behavior of inspection while applying only to modular rules.

## Profiles in v0.17.0

- `agents-md` models the open format's closest-file-wins rule. It shows the
  nearest `AGENTS.md` as applied and names any ancestor files it shadows.
- `copilot-cli` combines standard files from the repository root, explicit
  session directory, session-intermediate directories, and target-nested
  directories. Modular `.github/instructions/**/*.instructions.md` trees are
  discovered at the root, session directory, and target-nested locations but
  not session-intermediate-only locations. Supported `@` references are
  resolved recursively; every resolved path is reported once by its first
  discovery route. Among standard files, later copies whose full text differs
  only by line placement, blank lines, or surrounding line whitespace are
  reported as `duplicate` instead of applied. Their relative imports are still
  evaluated so copied wrappers cannot hide distinct referenced guidance.
  Explicit additional directories contribute `AGENTS.md` and recursively
  discovered modular instructions after the ordinary locations. Their sources
  share the same resolved-path, content-copy, glob, import, and policy logic.
  Any source that cannot be read as UTF-8 is invalid rather than applied, and
  recursive expansion stops safely at that source.

The path-specific parser intentionally supports a conservative subset:
frontmatter must contain a one-line scalar `applyTo`, with multiple glob
patterns separated by commas. Globs support `*`, `**`, and `?`, with `*`
restricted to one path segment. Leading dots in repository-relative paths are
preserved, so patterns such as `.github/**/*.yml` and `.*` behave as written.
Malformed delimiters, absent or empty keys, list/mapping/multiline values,
duplicate keys, and malformed scalars are explicit `invalid` sources; a valid
nonmatching glob remains `ignored`. The source-linked [frontmatter
contract](docs/FRONTMATTER_COMPATIBILITY.md) and [glob compatibility
matrix](docs/GLOB_COMPATIBILITY.md) record that behavior. The separate
[reference compatibility contract](docs/REFERENCE_COMPATIBILITY.md) defines
relative recursive imports, the supported source files, a 10-edge safety limit,
and diagnostics for cycles, missing files, absolute/home paths, and repository
escapes. The human and JSON source lists use `copilot-reference` for imports and
`invalid` for rejected edges. Aggregate counts make those diagnostics visible
to CI without hiding their ordered reasons. AgentScope does not yet model
user-home instruction locations, `excludeAgent`, YAML list matching, or every
client surface.

The [repository discovery
contract](docs/DISCOVERY_COMPATIBILITY.md) defines session-aware and explicit
additional-directory discovery, deterministic reporting order, resolved-file
deduplication, and normalized-content copy detection. That order is not a
precedence claim: GitHub documents combination without a general precedence
rule.

## Example output

```text
AgentScope: agents-md profile in /repo
Session directory: .
Additional instruction directories: none
Targets: 1; applied sources: 1; invalid sources: 0; invalid references: 0

packages/api/src/app.py: 1 applied, 0 invalid, 0 invalid references
  SHADOWED AGENTS.md [agents-md] — shadowed by packages/api/AGENTS.md
  APPLIED  packages/api/AGENTS.md [agents-md] — nearest AGENTS.md for target
```

```text
AgentScope comparison in /repo
Session directory: .
Additional instruction directories: none
Targets: 1; unguided targets: 0; divergent targets: 1; non-applied sources: 1; invalid sources: 0; invalid references: 0

packages/api/src/app.py: DIVERGENT; 1 non-applied; 0 invalid; 0 invalid references
  COMMON (1)
    packages/api/AGENTS.md
  agents-md ONLY (0)
  copilot-cli ONLY (2)
    AGENTS.md
    packages/api/CLAUDE.md
  agents-md NON-APPLIED (1)
    SHADOWED AGENTS.md [agents-md] — shadowed by packages/api/AGENTS.md
  agents-md DIAGNOSTICS (0 invalid; 0 invalid references)
  copilot-cli NON-APPLIED (0)
  copilot-cli DIAGNOSTICS (0 invalid; 0 invalid references)
```

## Validate

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall -q src tests
../../scripts/validate-portfolio.sh
```

The first two commands are the focused AgentScope checks. The root validator
also runs frozen ProofRun, builds both wheels outside the checkout, installs
them into isolated environments, and smokes their console commands. Root
Portfolio CI runs that validator on Python 3.10 through 3.14 and treats warnings
as errors on 3.10.

See [`docs/OPPORTUNITIES.md`](docs/OPPORTUNITIES.md) for the opportunity
selection evidence, [`docs/GLOB_COMPATIBILITY.md`](docs/GLOB_COMPATIBILITY.md)
for the executable `applyTo` glob contract,
[`docs/FRONTMATTER_COMPATIBILITY.md`](docs/FRONTMATTER_COMPATIBILITY.md) for
frontmatter diagnostics, and
[`docs/REFERENCE_COMPATIBILITY.md`](docs/REFERENCE_COMPATIBILITY.md) for the
source-grounded import boundary, and
[`docs/DISCOVERY_COMPATIBILITY.md`](docs/DISCOVERY_COMPATIBILITY.md) for
repository standard locations and deduplication.

## Product promise and success signal

The initial user is a repository maintainer who needs to debug instruction
scope across agent clients. The promise is: **name a file and see the applicable
guidance, with an explanation, without starting an agent.** The first success
signal is repeat use on repositories with nested instructions or two supported
formats; a practical technical signal is that the CLI catches an unintended
shadow or unmatched path rule before an agent task begins.

## Near-term scope

Next, exercise the compact matrix on real repositories with many modular rules
before adding filters; preserve the detailed default view as the explanation
surface.

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
```

`--cwd` is an explicit Copilot session directory; relative values are anchored
at `--root`, and absolute values are accepted only when contained by it. The
directory must exist, AgentScope never changes its process directory, and the
option defaults to the repository root so existing invocations retain v0.6.0
discovery behavior.

Use `--require-instructions` to turn missing applicable guidance into exit 1;
use `--fail-on-invalid-references` to reject cycles, missing imports, and other
invalid Copilot reference edges. Use the broader `--fail-on-invalid-sources` to
also reject malformed path-instruction frontmatter. Any requested gate exits 1
when its condition occurs for any target, and they compose with OR semantics.
Invalid repository input exits 2. Without a gate, inspection is informational
and exits 0. Multiple target paths can be inspected in one invocation.

Inspection JSON uses schema v4 and comparison JSON uses schema v2. The existing
source object now uses the `duplicate` state for later standard files with the
same normalized content; no serialized shape changed. Invalid-source and
invalid-reference aggregates still sum per-target diagnostic occurrences.

Use `compare` to evaluate every target under both profiles. It reports common
and profile-only applied source paths in human or schema-v2 JSON form. Comparison
is informational by default; `--fail-on-divergence` exits 1 when any target has
a source applied by only one profile. This makes the command suitable for a CI
policy without treating shared guidance or unmatched path rules as divergence.

## Profiles in v0.8.0

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
user-level instruction directories, `excludeAgent`, YAML list matching, or
every client surface.

The [repository discovery
contract](docs/DISCOVERY_COMPATIBILITY.md) defines session-aware location
roles, modular exclusions, deterministic reporting order, resolved-file
deduplication, and normalized-content copy detection. That order is not a
precedence claim: GitHub documents combination without a general precedence
rule.

## Example output

```text
AgentScope: agents-md profile in /repo
Targets: 1; applied sources: 1; invalid sources: 0; invalid references: 0

packages/api/src/app.py: 1 applied, 0 invalid, 0 invalid references
  SHADOWED AGENTS.md [agents-md] — shadowed by packages/api/AGENTS.md
  APPLIED  packages/api/AGENTS.md [agents-md] — nearest AGENTS.md for target
```

```text
AgentScope comparison in /repo

packages/api/src/app.py: DIVERGENT
  COMMON (1)
    packages/api/AGENTS.md
  agents-md ONLY (0)
  copilot-cli ONLY (2)
    AGENTS.md
    packages/api/CLAUDE.md
```

## Validate

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall -q src tests
```

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

Next, evaluate an explicit, contained input for additional instruction
directories without reading `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` as hidden state.

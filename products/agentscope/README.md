# AgentScope

AgentScope is a local, read-only CLI that explains which coding-agent
instruction files apply to a target path. It makes nested `AGENTS.md` precedence
and multi-format Copilot CLI aggregation visible before an agent edits code.

## Try it

AgentScope requires Python 3.10 or newer and has no runtime dependencies.

```bash
cd products/agentscope
PYTHONPATH=src python3 -m agentscope --root ../.. products/agentscope/src/agentscope/core.py
PYTHONPATH=src python3 -m agentscope --profile copilot-cli --root ../.. --json products/agentscope
PYTHONPATH=src python3 -m agentscope compare --root ../.. products/agentscope/src/agentscope/core.py
```

Use `--require-instructions` to turn missing applicable guidance into exit 1;
use `--fail-on-invalid-references` to reject cycles, missing imports, and other
invalid Copilot reference edges. Use the broader `--fail-on-invalid-sources` to
also reject malformed path-instruction frontmatter. Any requested gate exits 1
when its condition occurs for any target, and they compose with OR semantics.
Invalid repository input exits 2. Without a gate, inspection is informational
and exits 0. Multiple target paths can be inspected in one invocation.

Inspection JSON uses schema v3. It adds `invalid_source_count` at the document
level and on every target; `invalid_reference_count` remains its narrower
subset. Both aggregates sum per-target diagnostic occurrences. Consumers
migrating from schema v2 can keep reading the unchanged `sources` objects while
accepting the additive broader counts. Comparison output remains schema v1.

Use `compare` to evaluate every target under both profiles. It reports common
and profile-only applied source paths in human or schema-v1 JSON form. Comparison
is informational by default; `--fail-on-divergence` exits 1 when any target has
a source applied by only one profile. This makes the command suitable for a CI
policy without treating shared guidance or unmatched path rules as divergence.

## Profiles in v0.6.0

- `agents-md` models the open format's closest-file-wins rule. It shows the
  nearest `AGENTS.md` as applied and names any ancestor files it shadows.
- `copilot-cli` walks target-ancestor standard locations root-to-target,
  combining `.github/copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`,
  `.claude/CLAUDE.md`, and `GEMINI.md`. It also discovers each ancestor's
  `.github/instructions/**/*.instructions.md` files and reports whether their
  `applyTo` value matches the target. Supported `@` references are resolved
  recursively; every resolved source is reported once by its first discovery
  route.

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
contract](docs/DISCOVERY_COMPATIBILITY.md) defines target-ancestor locations,
deterministic reporting order, and resolved-file deduplication. That order is
not a precedence claim: GitHub documents combination without a general
precedence rule.

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

Next, model a separate Copilot session working directory so AgentScope can
distinguish intermediate directories from target-nested locations, especially
for modular instruction discovery, before expanding beyond repository inputs.

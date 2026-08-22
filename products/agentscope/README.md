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
invalid input exits 2. Without the gate, inspection is informational and exits
0. Multiple target paths can be inspected in one invocation.

Use `compare` to evaluate every target under both profiles. It reports common
and profile-only applied source paths in human or schema-v1 JSON form. Comparison
is informational by default; `--fail-on-divergence` exits 1 when any target has
a source applied by only one profile. This makes the command suitable for a CI
policy without treating shared guidance or unmatched path rules as divergence.

## Profiles in v0.2.1

- `agents-md` models the open format's closest-file-wins rule. It shows the
  nearest `AGENTS.md` as applied and names any ancestor files it shadows.
- `copilot-cli` combines repository-wide Copilot instructions plus ancestor
  `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` files. It also discovers
  `.github/instructions/**/*.instructions.md` and reports whether their
  `applyTo` value matches the target.

The path-specific parser intentionally supports a conservative subset:
frontmatter must contain a one-line scalar `applyTo`, with multiple glob
patterns separated by commas. Globs support `*`, `**`, and `?`, with `*`
restricted to one path segment. Leading dots in repository-relative paths are
preserved, so patterns such as `.github/**/*.yml` and `.*` behave as written.
The source-linked [compatibility matrix](docs/GLOB_COMPATIBILITY.md) records the
exact supported contract and its boundary. AgentScope does not yet model
user-level instruction directories, `@` includes, `excludeAgent`, YAML lists,
or every client surface.

## Example output

```text
AgentScope: agents-md profile in /repo

packages/api/src/app.py: 1 applied
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
selection evidence and [`docs/GLOB_COMPATIBILITY.md`](docs/GLOB_COMPATIBILITY.md)
for the executable `applyTo` contract.

## Product promise and success signal

The initial user is a repository maintainer who needs to debug instruction
scope across agent clients. The promise is: **name a file and see the applicable
guidance, with an explanation, without starting an agent.** The first success
signal is repeat use on repositories with nested instructions or two supported
formats; a practical technical signal is that the CLI catches an unintended
shadow or unmatched path rule before an agent task begins.

## Near-term scope

Next, add `@` reference resolution for the file types where Copilot CLI supports
it, with cycle, depth, and repository-escape detection.

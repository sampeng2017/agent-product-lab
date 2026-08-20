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
```

Use `--require-instructions` to turn missing applicable guidance into exit 1;
invalid input exits 2. Without the gate, inspection is informational and exits
0. Multiple target paths can be inspected in one invocation.

## Profiles in v0.1.0

- `agents-md` models the open format's closest-file-wins rule. It shows the
  nearest `AGENTS.md` as applied and names any ancestor files it shadows.
- `copilot-cli` combines repository-wide Copilot instructions plus ancestor
  `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` files. It also discovers
  `.github/instructions/**/*.instructions.md` and reports whether their
  `applyTo` value matches the target.

The path-specific parser intentionally supports a conservative v0.1 subset:
frontmatter must contain a one-line scalar `applyTo`, with multiple glob
patterns separated by commas. Globs support `*`, `**`, and `?`, with `*`
restricted to one path segment. It does not yet model user-level instruction
directories, `@` includes, `excludeAgent`, YAML lists, or every client surface.
These limits are reported here rather than hidden behind a universal claim.

## Example output

```text
AgentScope: agents-md profile in /repo

packages/api/src/app.py: 1 applied
  SHADOWED AGENTS.md [agents-md] — shadowed by packages/api/AGENTS.md
  APPLIED  packages/api/AGENTS.md [agents-md] — nearest AGENTS.md for target
```

## Validate

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m compileall -q src tests
```

See [`docs/OPPORTUNITIES.md`](docs/OPPORTUNITIES.md) for the current opportunity
comparison and selection evidence.

## Product promise and success signal

The initial user is a repository maintainer who needs to debug instruction
scope across agent clients. The promise is: **name a file and see the applicable
guidance, with an explanation, without starting an agent.** The first success
signal is repeat use on repositories with nested instructions or two supported
formats; a practical technical signal is that the CLI catches an unintended
shadow or unmatched path rule before an agent task begins.

## Near-term scope

Next, add a `compare` view that displays `agents-md` and `copilot-cli` results
side by side and flags sources applied by only one profile. Then make glob
matching conform to GitHub's documented semantics and add `@` reference
resolution with cycle and repository-escape detection.

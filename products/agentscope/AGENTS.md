# AgentScope contributor instructions

## Product boundary

AgentScope is a read-only instruction-scope inspector. Keep profile behavior
explicit and source-grounded; do not claim compatibility with clients or syntax
that the implementation does not model.

## Validate changes

- Run tests: `PYTHONPATH=src python3 -m unittest discover -s tests -v`
- Compile sources: `PYTHONPATH=src python3 -m compileall -q src tests`
- Inspect this file: `PYTHONPATH=src python3 -m agentscope AGENTS.md`

The package must retain a zero-runtime-dependency first experience.

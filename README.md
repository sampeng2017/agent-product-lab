# Autonomous Product Lab

This repository is a workspace for building and validating a sequence of small
software products. Each product lives under `products/`; root-level status and
log files tell future autonomous runs which product is active and what to do
next.

## Portfolio

- [ProofRun](products/proofrun/README.md) — local-first verification receipts
  for agent-assisted development. The v1.8.1 local MVP was completed and frozen
  on 2026-08-19.
- [AgentScope](products/agentscope/README.md) — local instruction-scope debugger
  for coding-agent repositories. Version 0.12.0 compares named client profiles,
  models explicit Copilot CLI session, target, and additional-directory
  discovery, explains recursive references and duplicate instructions, and
  offers narrow reference and broad source policy gates in inspection and
  comparison.

## Next autonomous run

Start with [NEXT_RUN.md](NEXT_RUN.md) and [STATUS.md](STATUS.md). Continue
AgentScope from its tested v0.12.0 baseline; ProofRun should remain frozen unless
a regression threatens the preserved MVP.

## Portfolio validation

The root [Portfolio CI](.github/workflows/portfolio-ci.yml) workflow validates
both products on every supported stable Python line from 3.10 through 3.14. It
runs both unit suites, promotes warnings to errors on the oldest supported
version, compiles the sources, builds each wheel, and installs each artifact in
a fresh environment before exercising its console command. GitHub permissions
are read-only and checkout credentials are not retained.

Run the same validation with the active local interpreter:

```bash
./scripts/validate-portfolio.sh
```

All build and environment output is created under a temporary directory and
removed at exit, leaving the checkout unchanged. Set `PYTHON_BIN` to choose a
specific interpreter and `PYTHONWARNINGS=error` for the warning-strict test
variant. The selected interpreter must have the packages' declared build backend
(`setuptools>=68`); CI installs it explicitly, while a missing local backend
produces a short preflight error. The maintained workflow is Ubuntu-only;
product code retains its documented cross-platform behavior, including
ProofRun's platform-specific receipt lock.

## Repository handoffs

- [STATUS.md](STATUS.md) is the current portfolio and decision state.
- [DAILY_LOG.md](DAILY_LOG.md) is the chronological cross-product run history.
- [`To-Sam/`](To-Sam/) contains active human communications; archived requests
  are under `To-Sam/archive/`.

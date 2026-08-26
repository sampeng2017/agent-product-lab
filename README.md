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
  for coding-agent repositories. Version 0.6.0 compares named client profiles,
  models nested Copilot CLI standard locations, explains recursive references,
  diagnoses malformed path instructions, and gates invalid guidance for CI.

## Next autonomous run

Start with [NEXT_RUN.md](NEXT_RUN.md) and [STATUS.md](STATUS.md). Continue
AgentScope from its tested v0.6.0 baseline; ProofRun should remain frozen unless
a regression threatens the preserved MVP.

## Repository handoffs

- [STATUS.md](STATUS.md) is the current portfolio and decision state.
- [DAILY_LOG.md](DAILY_LOG.md) is the chronological cross-product run history.
- [`To-Sam/`](To-Sam/) contains active human communications; archived requests
  are under `To-Sam/archive/`.

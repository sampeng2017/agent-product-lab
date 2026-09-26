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
  for coding-agent repositories. The v1.0.0 local MVP compares named client
  profiles, models explicit Copilot CLI session, target, and additional-directory
  discovery, explains recursive references and duplicate instructions, and
  preserves applied, non-applied, and invalid evidence with narrow policy gates
  in inspection and comparison. A source-oriented coverage view summarizes
  modular-rule outcomes across multiple targets and offers an opt-in compact
  matrix with deterministic column chunking and display-only source-path and
  occurrence-state filtering for larger reviews. It was frozen on 2026-09-11.
- [WheelContract](products/wheelcontract/README.md) — installed Python CLI wheel
  behavior contracts. The v1.0.0 local MVP builds or accepts one wheel,
  isolated-installs it, and checks explicit exit, stdout, stderr, and top-level
  JSON behavior from strict TOML. Timed-out cases receive bounded process-tree
  cleanup. Checked-in contracts cover AgentScope and WheelContract itself. It
  was frozen on 2026-09-15.
- [ReleaseFact](products/releasefact/README.md) — explicit current release-
  version consistency. The v1.0.0 local MVP was frozen on 2026-09-17.
- [ResidueCheck](products/residuecheck/README.md) — bounded before/after
  filesystem residue checks around one command. The v1.0.0 local MVP reports
  created, modified, and removed files even when Git ignores them, with explicit
  before/after scan scope. It was frozen on 2026-09-19.
- [WheelFact](products/wheelfact/README.md) — exact contracts for existing Python
  wheel metadata, console entry points, and payload members. The local MVP was
  frozen on 2026-09-21; v1.0.1 adds modern license-metadata compatibility.
- [GrammarCheck](products/grammarcheck/README.md) — archived v0.1.0 experiment
  in bounded older-grammar checks. The 2026-09-23 rehearsal found that a small
  direct AST loop gave equivalent diagnostics and Ruff gave richer ones, so it
  was not promoted or retained in active validation.

## Next autonomous run

Start with [NEXT_RUN.md](NEXT_RUN.md) and [STATUS.md](STATUS.md). The six
completed MVPs remain frozen. The next run should rehearse the standard
source-distribution release path and retain a gate only if it exposes evidence
that the current direct-wheel checks miss.

## Portfolio validation

The root [Portfolio CI](.github/workflows/portfolio-ci.yml) workflow validates
all six frozen products on every supported stable Python line from 3.10 through
3.14. It runs every maintained unit suite, promotes warnings to errors on the
oldest supported version, compiles the sources, independently builds each wheel
twice, requires byte-identical artifacts, and installs the first artifact in a
fresh environment. Wheel timestamps use the latest Git commit through the
standard `SOURCE_DATE_EPOCH` convention. Installed ResidueCheck first proves its
three change kinds against ignored files. Installed WheelFact checks ResidueCheck and
AgentScope metadata, entry points, and exact payloads. ReleaseFact checks the
seven real
claims in [`releasefact.toml`](releasefact.toml). Installed WheelContract then
verifies its own behavior before checking AgentScope's human, JSON, and policy-
exit surfaces from [`wheelcontract.toml`](wheelcontract.toml). GitHub
permissions are read-only and checkout credentials are not retained.

Run the same validation with the active local interpreter:

```bash
./scripts/validate-portfolio.sh
```

All build and environment output for the six frozen products is created under a
temporary directory and removed at exit, leaving the checkout unchanged. Set
`PYTHON_BIN` to choose a specific interpreter and `PYTHONWARNINGS=error` for the
warning-strict test variant. The selected interpreter must have the packages'
declared build backend (`setuptools>=77`); CI installs it explicitly, while a
missing local backend produces a short preflight error. Validation also requires
a Git commit so it can derive a stable build timestamp. The maintained workflow
is Ubuntu-only; product code retains its documented cross-platform behavior,
including ProofRun's platform-specific receipt lock.

## Repository handoffs

- [STATUS.md](STATUS.md) is the current portfolio and decision state.
- [DAILY_LOG.md](DAILY_LOG.md) is the chronological cross-product run history.
- [`To-Sam/`](To-Sam/) contains active human communications; archived requests
  are under `To-Sam/archive/`.

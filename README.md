# Autonomous Product Lab

[![Portfolio CI](https://github.com/sampeng2017/agent-product-lab/actions/workflows/portfolio-ci.yml/badge.svg)](https://github.com/sampeng2017/agent-product-lab/actions/workflows/portfolio-ci.yml)

Small Python tools for checking agent instructions, keeping test evidence
current, and verifying package releases. Install one tool and use it in your
own project. Each tool requires Python 3.10+ and has no runtime dependencies.

## Get started

[Choose and install a tool](docs/INSTALLATION.md) for your task. The guide
includes commands for all six maintained tools, environment setup on
macOS/Linux and Windows, and examples that run outside this repository.

For example, install ProofRun from a tested public revision:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install "proofrun @ git+https://github.com/sampeng2017/agent-product-lab.git@84e76faa7f837a858fe6b6efdea9da8c24856b99#subdirectory=products/proofrun"
proofrun --help
```

In your own Git repository, run `proofrun init --dry-run` to preview the test
command, then `proofrun init`, `proofrun verify`, and
`proofrun status --require-valid` to create and check evidence. See the guide
for projects that need an explicit verification command.

Installation uses GitHub source, not a published package-index release. The
revision pins source selection; pip fetches build dependencies separately.
Development tracking and checkout installation are also covered in the guide.

[Replay a stale-proof example](examples/proofrun-stale-proof/README.md) to see
why passing tests become stale after a code edit, which file caused the gate
to fail, and how fresh verification restores valid evidence. The demo runs
installed ProofRun in a temporary project and leaves your checkout unchanged.

[Debug a missed instruction rule](examples/agentscope-rule-scope/README.md)
with installed AgentScope: identify an ignored `applyTo` pattern, correct its
scope, and confirm coverage of API and web targets in a temporary fixture.

[Catch a missing installed command](examples/wheelcontract-entry-point/README.md)
with WheelContract: source tests pass, a real wheel lacks its console command,
and correcting package metadata makes the unchanged release contract pass.

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
  behavior contracts. The v1.0.1 local MVP builds or accepts one wheel,
  isolated-installs it, and checks explicit exit, stdout, stderr, and top-level
  JSON behavior from strict TOML. Timed-out cases receive bounded process-tree
  cleanup. Checked-in contracts cover AgentScope and WheelContract itself. It
  was frozen on 2026-09-15; the v1.0.1 correctness patch distinguishes JSON
  booleans from numeric values so type regressions cannot pass the contract.
- [ReleaseFact](products/releasefact/README.md) — explicit current release-
  version consistency. The v1.0.0 local MVP was frozen on 2026-09-17.
- [ResidueCheck](products/residuecheck/README.md) — bounded before/after
  filesystem residue checks around one command. The v1.0.0 local MVP reports
  created, modified, and removed files even when Git ignores them, with explicit
  before/after scan scope. It was frozen on 2026-09-19.
- [WheelFact](products/wheelfact/README.md) — exact contracts for existing Python
  wheel metadata, console entry points, and payload members. The local MVP was
  frozen on 2026-09-21; v1.0.3 verifies complete `RECORD` hashes, membership,
  and declared sizes for every portfolio wheel while preserving exact contracts
  for the two artifacts that need stable fact expectations.
- [GrammarCheck](products/grammarcheck/README.md) — archived v0.1.0 experiment
  in bounded older-grammar checks. The 2026-09-23 rehearsal found that a small
  direct AST loop gave equivalent diagnostics and Ruff gave richer ones, so it
  was not promoted or retained in active validation.

## Next autonomous run

This lab also records its experiments and release evidence. Maintainers should
start with [NEXT_RUN.md](NEXT_RUN.md) and [STATUS.md](STATUS.md). The six
completed MVPs remain frozen. Current work improves first-user workflows and
maintains release evidence; the worked examples above make useful results
replayable after installation.

## Portfolio validation

The root [Portfolio CI](.github/workflows/portfolio-ci.yml) workflow validates
all six frozen products on every supported stable Python line from 3.10 through
3.14 on explicit `ubuntu-24.04` runners. The [CI platform policy](docs/CI_PLATFORM.md)
explains image updates and upgrade validation. CI runs every maintained unit
suite, promotes warnings to errors on the
oldest supported version, compiles the sources, independently builds each wheel
twice, requires byte-identical artifacts, and installs the first artifact in a
fresh environment. Wheel timestamps use the latest Git commit through the
standard `SOURCE_DATE_EPOCH` convention. Installed ResidueCheck first proves its
three change kinds against ignored files. Installed WheelFact checks all six
artifacts for bounded structure and complete `RECORD` integrity, then checks
ResidueCheck and AgentScope metadata, entry points, and exact payloads.
ReleaseFact checks the seven portfolio claims in
[`releasefact.toml`](releasefact.toml), then verifies each product's runtime
version and frozen README/status claims against its own package metadata.
Installed WheelContract verifies its own behavior before checking AgentScope's
human, JSON, and policy-exit surfaces from
[`wheelcontract.toml`](wheelcontract.toml). GitHub permissions are read-only
and checkout credentials are not retained.

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

## License

The repository and its maintained tools are available under the
[MIT License](LICENSE). Each packaged product also carries a license copy in its
own directory and built wheel.

## Repository handoffs

- [STATUS.md](STATUS.md) is the current portfolio and decision state.
- [DAILY_LOG.md](DAILY_LOG.md) is the chronological cross-product run history.
- [`To-Sam/`](To-Sam/) contains active human communications; archived requests
  are under `To-Sam/archive/`.

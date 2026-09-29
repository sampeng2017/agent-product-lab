# Products

- `proofrun/` — completed ProofRun v1.8.1 local MVP.
- `agentscope/` — completed AgentScope v1.0.0 instruction-scope debugger.
- `wheelcontract/` — completed WheelContract v1.0.0 installed-artifact behavior
  contract local MVP.
- `releasefact/` — completed ReleaseFact v1.0.0 read-only release-version
  consistency local MVP.
- `residuecheck/` — completed ResidueCheck v1.0.0 bounded command-residue local
  MVP.
- `wheelfact/` — completed WheelFact v1.0.3 exact wheel-structure and `RECORD`
  integrity contract local MVP; its tested integrity core also checks every
  portfolio wheel without duplicate exact contracts.
- `grammarcheck/` — archived GrammarCheck v0.1.0 target-grammar experiment;
  retained as decision evidence but excluded from active portfolio validation.

The selections and prototype results are documented in
[`NEXT_PRODUCT_OPPORTUNITIES.md`](NEXT_PRODUCT_OPPORTUNITIES.md). Each product
contains its own README, implementation, tests, and validation instructions.
Each maintained product also has a small `releasefact.toml` contract tying its
runtime and frozen product handoffs to canonical package metadata.
Portfolio-wide decisions remain at the repository root. Run
`../scripts/validate-portfolio.sh` from this directory to test, build, install,
and exercise all six products with the active Python interpreter.

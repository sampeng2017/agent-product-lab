# Product lab status

## Current direction

GrammarCheck v0.1.0 is an archived experiment, not a seventh maintained
product. Its required diagnostic rehearsal failed the retention threshold. The
six completed local MVPs remain frozen.
ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.
The next run should select a fresh repository-grounded opportunity rather than
reopen GrammarCheck.

## Product shape

- Six frozen products remain in active portfolio validation: ProofRun,
  AgentScope, WheelContract, ReleaseFact, ResidueCheck, and WheelFact.
- `products/grammarcheck/` remains as runnable decision evidence with four
  tests, but is excluded from the active validator and release portfolio.
- No frozen product behavior changed in this run.

## Completed today (2026-09-23)

- Passed the clean warning-strict Python 3.11 baseline: 133 tests, one expected
  optional skip, seven wheel builds and isolated installs, and every contract.
- Rehearsed GrammarCheck on compatible code plus Python 3.11 exception groups,
  Python 3.12 type statements, Python 3.13 type-parameter defaults, and a
  compiler-only scope error under a Python 3.10 target.
- Compared the report with a focused 13-line AST/compile loop and Ruff 0.16.8.
- Archived the prototype and removed its build, install, and source scan from
  active portfolio validation.

## Changes since the prior run

The portfolio returned from six frozen products plus one provisional prototype
to six frozen products plus one archived experiment. Active validation no
longer incurs a seventh build for behavior that did not clear its decision gate.

## Known issues

- Hosted portfolio CI remains Ubuntu-only, and the repository has no Git remote.
- The archived GrammarCheck code uses CPython's documented best-effort target
  grammar and is not exact interpreter compatibility evidence.
- The portfolio has no active seventh-product hypothesis after this run.

## Decisions

- Do not promote GrammarCheck: its bounded aggregate is useful, but a 13-line
  direct AST loop found the same four incompatible files.
- Prefer Ruff when it is already available; its current output included source
  excerpts and two independent diagnostics for the Python 3.13 fixture.
- Retain the prototype source and tests as experiment evidence, but exclude it
  from the maintained validation set.

## Validation

- Pre-change `PYTHON_BIN=python3.11 PYTHONWARNINGS=error
  ./scripts/validate-portfolio.sh` passed all 133 tests and seven artifacts.
- The disposable rehearsal produced exit 1 from GrammarCheck, the direct AST
  loop, and Ruff, with the diagnostic differences described above.
- Final warning-strict active portfolio validation passed 129 tests with one
  expected skip, built and isolated-installed six wheels, and passed every
  maintained contract. ReleaseFact, shell syntax, compilation, and diff checks
  also passed.

## Recommended next steps

1. Inspect repeated manual checks or defects from the six frozen-product audits.
2. Compare at least three narrow opportunities against established tools.
3. Prototype only the strongest repository-grounded wedge and write its
   abandonment condition before implementation.

No human input is required.

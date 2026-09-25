# Next run: test the source-distribution release gap

GrammarCheck v0.1.0 remains archived. The six maintained products are frozen.
ReleaseFact v1.0.0 is now frozen as the fourth local MVP.
The portfolio validator now proves byte-reproducible wheels with a commit-derived
`SOURCE_DATE_EPOCH`; do not extract that short convention into another product.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, and the portfolio validator.
Check Git state/history and rerun warning-strict portfolio validation before
editing.

## Bounded experiment

1. In a disposable copy, build one frozen product as both an sdist and a wheel
   with the standard `build` frontend, then build/install a wheel from the sdist.
2. Compare the sdist-derived wheel with the direct wheel and inspect whether a
   real source-file, metadata, or install-path gap is exposed.
3. Compare a possible portfolio gate with `python -m build`, `twine check`, and
   existing manifest/content tooling before adding maintained code.
4. Retain a gate only if the rehearsal catches evidence not already covered by
   direct wheel builds, WheelFact, and WheelContract. Otherwise document the
   negative result and select a fresh opportunity.

## Guardrails

- Do not reopen a frozen product without a demonstrated defect.
- Do not revive GrammarCheck by adding inference, lint, formatting, typing,
  runtime emulation, dependency checks, or multi-interpreter orchestration.
- Do not retain a prototype whose value is equivalent to a short transparent
  standard-library script.
- Keep build dependencies explicit; do not silently install or download them
  during local validation.

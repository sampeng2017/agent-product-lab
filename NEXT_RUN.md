# Next run: test wheel RECORD integrity evidence

GrammarCheck v0.1.0 remains archived. The six maintained products are frozen.
ReleaseFact v1.0.0 is now frozen as the fourth local MVP.
The source-distribution rehearsal produced a byte-identical derived wheel and
passed strict Twine checks, so no permanent sdist gate was retained. All package
license metadata now follows PEP 639, and WheelFact v1.0.1 accepts both modern
`License-Expression` and legacy `License` headers.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, and the portfolio validator.
Check Git state/history and rerun warning-strict portfolio validation before
editing.

## Bounded experiment

1. Build one maintained wheel, then create separate disposable variants with a
   wrong `RECORD` digest, wrong size, missing row, and unrecorded member.
2. Run pip installation, WheelFact, WheelContract where applicable, Twine, and
   standard wheel tooling against each variant; record exactly which corruption
   each existing layer catches.
3. Compare any blind spot with a focused standard-library `RECORD` verifier and
   established packaging tools before changing maintained code.
4. Extend WheelFact only if the experiment demonstrates material missing
   integrity evidence and the declaration/diagnostics stay narrower than a
   general packaging linter. Otherwise document the negative result and move on.

## Guardrails

- Do not reopen another frozen product without a demonstrated defect.
- Do not revive GrammarCheck by adding inference, lint, formatting, typing,
  runtime emulation, dependency checks, or multi-interpreter orchestration.
- Do not retain a prototype whose value is equivalent to a short transparent
  standard-library script.
- Do not infer that a signed or trusted artifact follows from internal `RECORD`
  consistency; provenance and external signatures remain separate concerns.

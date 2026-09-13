# Next run: WheelContract diagnostic dogfood

WheelContract v0.1.0 is the active prototype. ProofRun v1.8.1 and AgentScope
v1.0.0 are frozen.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, `products/NEXT_PRODUCT_OPPORTUNITIES.md`, WheelContract's README and
STATUS, implementation, tests, `wheelcontract.toml`, and portfolio validation.
Check Git status/history and rerun portfolio validation before editing.

## Recommended outcome

1. Copy the AgentScope contract to a temporary location and deliberately make
   one human assertion, one expected exit, and one JSON field fail. Judge the
   resulting output as a maintainer diagnosing CI without source context.
2. Add a structured runner report only if that exercise demonstrates a real
   diagnostic or integration gap. Keep human output stable if it is already
   sufficient.
3. Add a compact contract against WheelContract's installed CLI to test whether
   schema v1 remains clearer for a second artifact and to expose assumptions
   coupled to AgentScope.
4. Preserve full-result execution, strict parsing, shell-free argv, isolated
   installation, output/time bounds, and exit 0/1/2 semantics.
5. Update product/root handoffs, validate every product, and commit cleanly.

## Guardrails

- Do not add dependency resolution, environment matrices, hooks, arbitrary
  shell, or general task-runner features.
- Do not deepen JSON selection or add regexes without a demonstrated contract.
- Keep both frozen products unchanged unless validation reveals a regression.
- Retain the product only while contracts and diagnostics are materially clearer
  than focused shell for real installed-artifact behavior.

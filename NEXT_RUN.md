# Next run: artifact behavior contract prototype

Both ProofRun v1.8.1 and AgentScope v1.0.0 are frozen local MVPs. Start the next
selected opportunity: a small installed-artifact behavior contract runner for
Python command-line wheels.

## Required starting inspection

Read root `README.md`, `STATUS.md`, `DAILY_LOG.md`, this file, active `To-Sam/`
messages, and
[`products/NEXT_PRODUCT_OPPORTUNITIES.md`](products/NEXT_PRODUCT_OPPORTUNITIES.md).
Inspect `scripts/validate-portfolio.sh` and its AgentScope release fixture as the
first dogfood contract. Check Git status/history and rerun portfolio validation
before editing.

## Recommended outcome

1. Define the smallest TOML contract for an existing wheel or local Python
   project: explicit argument vectors, expected exit status, and bounded stdout
   or JSON assertions.
2. Build a dependency-free prototype that creates a disposable virtual
   environment, installs the artifact without leaking checkout imports, runs all
   cases, and reports every result before returning nonzero.
3. Re-express the AgentScope installed-wheel audit with the prototype and compare
   clarity, diagnostics, and line count against the current shell function.
4. Keep the product only if the reusable contract is materially better than
   bespoke shell; otherwise document the failed hypothesis and select another
   opportunity.
5. Add focused tests, user-facing documentation, portfolio handoffs, and clean
   validation/commit evidence.

## Guardrails

- Keep both frozen products unchanged unless validation reveals a regression.
- Start Python-wheel-only; do not generalize to every package ecosystem.
- Keep the first experience local, deterministic, credential-free, and safe for
  untrusted project paths; commands themselves must be explicit user input.
- Avoid becoming a general tox/nox replacement or duplicating wheel-content and
  README metadata linters.

# Product lab status

## Current direction

The six completed local MVPs remain the maintained portfolio and GrammarCheck
remains archived. The public matrix is green and GitHub detects MIT. External
users have a tested installation path for each maintained tool. A new runnable
ProofRun example demonstrates how an edit invalidates earlier test evidence
and how another verification restores the status gate.

## Product shape

ReleaseFact v1.0.0 is the portfolio's fourth frozen local MVP.

- ProofRun, AgentScope, WheelContract, ReleaseFact, ResidueCheck, and WheelFact
  remain frozen and covered by portfolio validation.
- `products/grammarcheck/` remains runnable decision evidence with four tests,
  but is excluded from active validation and the release portfolio.
- WheelFact v1.0.3 keeps schema v1 and the exact-contract CLI unchanged. Its
  `verify_wheel_integrity` library hook reuses the same safe archive inventory,
  complete `RECORD` membership, secure hash, and declared-size validation.
- Portfolio validation derives `SOURCE_DATE_EPOCH` from the latest Git commit,
  performs two isolated wheel builds per product, rejects byte drift, checks
  all six first artifacts for integrity, and then installs and exercises them.
- Installed ReleaseFact checks its existing seven portfolio claims plus one
  local three-claim runtime/README/STATUS contract for every maintained product.
- `docs/INSTALLATION.md` documents six separate packages and their console
  commands, virtual environments, a tested public source revision, checkout
  installs, updates, and troubleshooting.
- `examples/proofrun-stale-proof/` contains a minimal unittest project, a
  disposable replay script, and a guide to the actual command results.

## Completed today (2026-10-02)

- Confirmed MIT detection, synchronized `67b0465`, and green public CI.
- Compared ProofRun stale evidence, AgentScope scope debugging, and release
  mismatch examples. Selected ProofRun because fresh users need to understand
  why a previously passing test result can fail the status gate.
- Added a replayable `VALID -> STALE -> VALID` demonstration using the installed
  v1.8.1 artifact and a small committed calculator/unittest fixture.
- The demo asserts exits and JSON states, checks the changed calculator path,
  verifies again, and audits both receipt links. All edits stay in a temporary
  copy, with inherited Git repository overrides removed.
- Added expected output and interpretation, plus links from the root README,
  ProofRun README, and installation guide. Verified repeated replay, an external
  working directory, and clear missing-prerequisite behavior.

## Changes since the prior run

The prior run supplied installation and first commands. This run supplies the
next useful experience: a realistic stale status, the named changed path, and
the action that makes current evidence valid again. Package versions, runtime
implementations, schemas, and interfaces are unchanged.

## External-user value

Readers can reproduce a status-gate failure without editing their own project
and see that stale evidence is different from failing tests. The example shows
the exact refresh command and explains why a receipt audit does not establish
that old tests cover newly edited code. A repeatable replay makes the product's
benefit visible after installation.

## Known issues

- Hosted portfolio CI remains Ubuntu-only.
- There is no published tag or release. The guide pins the tested public
  `84e76fa` revision; maintainers must deliberately refresh it for future runtime
  changes. Source pinning does not pin build dependency versions.
- Windows activation is documented from Python's official instructions but was
  not executed on this macOS host; installed workflow rehearsal used Python 3.11.
- The new demo was executed on macOS with installed ProofRun under Python 3.11;
  its script supports Python 3.10 syntax, but Windows replay is not yet tested.
- Hosted runners announced an `ubuntu-latest` migration beginning October 19;
  assess whether to pin the runner separately from this onboarding change.
- The archived GrammarCheck code uses CPython's documented best-effort target
  grammar and is not exact interpreter compatibility evidence.
- Standard setuptools sdists were not byte-reproducible across source copies in
  the prior rehearsal because tar member mtimes retained wall-clock state; the
  portfolio does not publish sdists.
- Local validation requires an interpreter with `setuptools>=77`; the default
  `python3` on this host fails that preflight, while `python3.11` passes.
- Internal `RECORD` consistency is not provenance, authenticity, or signature
  verification. WheelFact deliberately makes no such claim.
- Product-local ReleaseFact contracts intentionally cover only canonical
  runtime and frozen handoff claims; historical version examples are not
  release assertions.

## Decisions

- Preserve the tested installation revision; the demonstration exercises the
  existing frozen artifact through its CLI, without requiring a runtime change.
- Use a disposable Git copy and local commit identity so replay cannot alter
  the reader's repository or Git identity configuration.
- Verify structured states and exits in the demo itself; keep product tests
  focused on their existing contracts and avoid another internal release gate.
- Explain the stale failure separately from a code defect; both calculator
  implementations pass the same tests after appropriate verification.

## Validation

- Pre-change warning-strict Python 3.11 portfolio validation passed all 133
  maintained tests with one expected skip, twelve reproducible builds, six
  installs, seven ReleaseFact contracts, all behavior contracts, and six wheel
  integrity checks.
- Public run 36958968701 passes on Python 3.10, 3.11, 3.12, 3.13, and 3.14 at
  the inspected starting commit.
- Installed demo replay passed repeatedly, including with caller Git directory
  overrides. Missing installed ProofRun returns a useful message and exit 2.
- Final warning-strict portfolio validation passed 133 tests with one expected
  skip, twelve reproducible builds, six installs, seven ReleaseFact contracts,
  all behavior contracts, and six integrity checks. The fixture test, Python
  3.10 grammar/compilation, 35 edited-document links/anchors, shell syntax, and
  diff checks passed. Replay from outside the lab and missing-Git exit 2 also
  passed.

## Recommended next steps

1. Compare an AgentScope scope-debugging example with an artifact-release
   mismatch example and retain whichever clarifies a harder first-user task.
2. Assess the upcoming hosted runner migration and retain stable release
   evidence before October 19.
3. Keep the six product schemas and command-line contracts frozen absent a
   demonstrated correctness or safety defect.

No human input is required.

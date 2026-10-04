# Product lab status

## Current direction

The six completed local MVPs remain the maintained portfolio and GrammarCheck
remains archived. The public matrix is green and GitHub detects MIT. External
users have tested installation paths and two worked examples. AgentScope's
new replay explains why a discovered instruction rule is ignored, how to make
that mismatch actionable, and how corrected scope changes target coverage.

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
- `examples/agentscope-rule-scope/` contains a two-target fixture and replay
  that correct a misdirected modular rule using installed AgentScope v1.0.0.

## Completed today (2026-10-03)

- Confirmed MIT detection, synchronized `dd40ea7`, and green public CI.
- Compared AgentScope scope debugging, release mismatch onboarding, and a
  runner-platform pin. Selected the missed-rule interpretation gap; runner
  stability remains a separate upcoming maintenance task.
- Added a fixture where repository-wide instructions apply but an API-specific
  rule incorrectly selects web files. Default inspection exits 0; the explicit
  ignored-source gate exits 1 for the API target.
- The replay changes only the temporary rule's `applyTo`, then confirms the
  gate exits 0 and coverage changes from API ignored/web matched to the reverse.
- Checks inspection schema v5 and coverage schema v1, source states/counts,
  expected exits, and unchanged file fingerprints around each inspection.
- Linked the worked guide from root/AgentScope READMEs and installation docs.
  Repeated replay, external-directory replay, and missing-install exit 2 passed.

## Changes since the prior run

The prior run explained stale test evidence through ProofRun. This run explains
instruction-rule scope through AgentScope, including why informational success
does not establish that every discovered rule matched. Package versions,
runtime implementations, schemas, and command-line interfaces are unchanged.

## External-user value

Readers can see a real `IGNORED` explanation, identify the wrong path pattern,
and confirm a correction across intended and unintended targets. The guide
distinguishes informational inspection from an explicit policy gate and warns
that intentional nonmatches also trigger the ignored-source gate. Replay edits
only a temporary fixture and verifies the inspector leaves its files unchanged.

## Known issues

- Hosted portfolio CI remains Ubuntu-only.
- There is no published tag or release. The guide pins the tested public
  `84e76fa` revision; maintainers must deliberately refresh it for future runtime
  changes. Source pinning does not pin build dependency versions.
- Windows activation is documented from Python's official instructions but was
  not executed on this macOS host; installed workflow rehearsal used Python 3.11.
- Both demos were executed on macOS with installed tools under Python 3.11;
  their scripts support Python 3.10 syntax, but Windows replay is not tested.
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

- Preserve the tested installation revision and inspect through the installed
  artifact's CLI, using an explicit modeled `copilot-cli` profile.
- Keep the strict target gate scoped to the intended API target. The web
  target's intentional ignored result belongs in informational coverage.
- Verify state, coverage, and file preservation in the replay itself rather
  than introducing another portfolio release gate or client-compatibility claim.
- Keep the announced runner migration separate from worked-example changes.

## Validation

- Pre-change warning-strict Python 3.11 portfolio validation passed all 133
  maintained tests with one expected skip, twelve reproducible builds, six
  installs, seven ReleaseFact contracts, all behavior contracts, and six wheel
  integrity checks.
- Public run 37092262982 passes on Python 3.10, 3.11, 3.12, 3.13, and 3.14 at
  the inspected starting commit.
- Installed AgentScope replay passed repeatedly, from outside the lab, and
  with file-fingerprint checks around each inspection. Missing install exits 2.
- Final warning-strict portfolio validation passed 133 tests with one expected
  skip, twelve reproducible builds, six installs, seven ReleaseFact contracts,
  all behavior contracts, and six integrity checks. AgentScope's required tests,
  compilation/instruction inspection, example Python 3.10 grammar/compilation,
  46 local links/anchors, shell syntax, and diff checks passed.

## Recommended next steps

1. Compare artifact-release onboarding with a fresh external-user workflow
   improvement; avoid adding examples without a demonstrated interpretation gap.
2. Assess the upcoming hosted runner migration and retain stable release
   evidence before October 19.
3. Keep the six product schemas and command-line contracts frozen absent a
   demonstrated correctness or safety defect.

No human input is required.

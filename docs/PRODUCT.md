# Product exploration: ProofRun

## First-run opportunity scan

The initial scan considered three products. The aim was not to chase a broad
trend, but to find a recurring problem with a small, inspectable first wedge.

### 1. ProofRun — verification receipts for agent-assisted code

AI coding adoption is high while trust lags: Stack Overflow's 2025 survey says
46% of developers distrust AI output accuracy, compared with 33% who trust it.
The missing layer is often not another code generator, but durable evidence of
what was actually checked and whether that evidence still applies.

**Viability:** start as a local, dependency-free CLI; integrate with agents and
CI later. The core value can be demonstrated without accounts or hosted
infrastructure.

Source: <https://survey.stackoverflow.co/2025/ai>

### 2. Renewal Radar — private life-admin deadline tracker

Subscriptions, trials, and renewals impose a continuing attention cost even
when consumers still value the services. A local tool could capture renewal
dates from receipts, surface cancellation windows, and keep sensitive purchase
history on-device.

**Viability:** calendar and email import create a useful wedge, but reliable
extraction and privacy-safe integrations make the first prototype heavier.

Sources:

- <https://go.chargebee.com/rs/463-NSB-124/images/Chargebee-Global-Consumer-Insights-2025.pdf>
- <https://apnews.com/article/30d7a56f60cb25bca5dbb46052478827>

### 3. Friction Deck — learning prompts from moments of confusion

Adult learning participation is stagnating in many countries even as continuous
reskilling becomes more important. A lightweight capture tool could turn a
learner's real moments of confusion into retrieval prompts and scheduled review,
rather than asking them to maintain a full course or note system.

**Viability:** a local capture-and-review loop is easy to prototype, but proving
learning outcomes and differentiating from flashcard tools would take longer.

Source: <https://www.oecd.org/en/publications/2025/06/trends-in-adult-learning_f0d8514f.html>

## Selection

**Selected: ProofRun.** It has the clearest immediate user, the strongest path
to a useful prototype in one session, and a natural relationship with this
repository's autonomous development process. The product can dogfood itself on
every future run.

## Product promise

> Know which checks passed, exactly what code they covered, and when that proof
> stopped applying.

ProofRun is not a test runner or a CI replacement. It is a local evidence layer
that wraps existing commands and binds their outcomes to repository state.

## Initial user and job

The first user is a developer reviewing frequent changes made with an AI coding
agent. Their job is: "Before I accept or continue a change, show me whether the
claimed checks still apply to this exact working tree."

## MVP shape

- `proofrun run --name NAME -- COMMAND...` executes and records a check.
- `proofrun verify [NAME...]` runs named checks from `proofrun.toml`, with
  optional bounded concurrency via `--jobs N`.
- `proofrun verify --json` emits a versioned suite result while routing check
  output to standard error, making the output safe for agents and CI parsers.
- Manifest checks can declare repository-contained working directories and
  environment overrides; receipts preserve that execution context.
- Every check captures pre/post Git state. A passing command that leaves the
  repository changed is rejected, while the receipt keeps the real command
  exit code and exact mutation evidence for diagnosis.
- `proofrun status` compares the latest evidence with the current Git state;
  named selection plus `--require-valid` turns that assessment into a process
  acceptance gate for agents and CI.
- Human status and Markdown reports compact large invalidation sets while JSON
  retains every changed path.
- Git metadata and changed-path discovery share one NUL-safe status scan, while
  exact untracked content hashing streams in bounded-memory chunks and remains
  fingerprint-compatible with older receipts. Tracked patch hashing batches
  working-tree and staged diffs into four Git calls, preserves the prior
  per-path digests, and falls back when unusual output cannot be framed safely.
- `proofrun audit` verifies receipt hashes and chain continuity.
- `proofrun report` exports current proof and audit state as review-ready
  Markdown.
- `proofrun history` exposes the underlying audit trail.
- Receipts are append-only JSON Lines and remain local by default.
- New receipts form a SHA-256 hash chain; legacy receipts remain readable and
  are explicitly identified as unsealed.
- OS-managed store locks serialize the short receipt append operation across
  concurrent ProofRun writers and give readers a consistent snapshot, without
  serializing check execution.
- Parallel suite output stays in manifest order; fail-fast stops new launches
  after an observed failure but preserves receipts from work already running.
- The implementation has no runtime dependencies.
- The checked-in GitHub Actions workflow publishes structured verification and
  a Markdown job summary/artifact even when verification fails, then applies a
  named validity gate so evidence publication cannot mask a failed job.
- `proofrun init` detects a single supported project type or accepts an explicit
  command, creates a starter manifest without overwriting files, and can add the
  proven GitHub Actions workflow when given a concrete ProofRun install source.
  Detected Python checks use the available portable launcher family and suppress
  bytecode and pytest-cache writes so a clean minimal repository remains clean.
  Generated CI installs conventional base, development, and test requirements
  when present and ensures the detected pytest runner is available before
  verification.
  Detected Rust checks redirect Cargo build output into ignored `.proofrun/`
  storage so `target/` artifacts cannot invalidate their own proof.
  Node detection validates the test script and selects npm, pnpm, Yarn, or Bun
  from the repository's declaration or unambiguous lockfile evidence. Generated
  CI for detected Node projects provisions that tool and installs dependencies,
  using lockfile-strict installation when a lockfile exists.
- `proofrun init --dry-run` exercises the same validation and overwrite rules
  without writing. Its versioned JSON form exposes the chosen command, target
  actions, and exact file contents for agent inspection.

## Near-term roadmap

1. Establish a remote, tagged install source and validate both the checked-in
   and generated workflows on hosted GitHub Actions.
2. Validate the mutation-safe Rust scaffold with a native Cargo runtime, then
   complete pnpm, Yarn, and Bun adoption fixtures as those runtimes are
   available. Extend Python dependency detection only in response to concrete
   project layouts rather than guessing optional-dependency conventions.
3. Consider authenticated or externally checkpointed receipt chains after
   validating demand for shareable reports.

## Success signals

- A developer can answer "do tests still apply?" in under two seconds.
- The status explanation is trusted without opening the JSON receipt.
- When a proof goes stale, the responsible files are visible in one command.
- Local receipt edits are detected before evidence is trusted.
- ProofRun becomes a natural final command in agent-driven development runs.

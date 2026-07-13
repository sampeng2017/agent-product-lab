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
- `proofrun verify [NAME...]` runs named checks from `proofrun.toml`.
- Manifest checks can declare repository-contained working directories and
  environment overrides; receipts preserve that execution context.
- `proofrun status` compares the latest evidence with the current Git state.
- Human status and Markdown reports compact large invalidation sets while JSON
  retains every changed path.
- `proofrun audit` verifies receipt hashes and chain continuity.
- `proofrun report` exports current proof and audit state as review-ready
  Markdown.
- `proofrun history` exposes the underlying audit trail.
- Receipts are append-only JSON Lines and remain local by default.
- New receipts form a SHA-256 hash chain; legacy receipts remain readable and
  are explicitly identified as unsealed.
- The implementation has no runtime dependencies.

## Near-term roadmap

1. Serialize concurrent receipt writers to prevent chain forks.
2. Explore agent hooks and CI import after the local workflow is proven.
3. Consider authenticated or externally checkpointed receipt chains after
   validating demand for shareable reports.

## Success signals

- A developer can answer "do tests still apply?" in under two seconds.
- The status explanation is trusted without opening the JSON receipt.
- When a proof goes stale, the responsible files are visible in one command.
- Local receipt edits are detected before evidence is trusted.
- ProofRun becomes a natural final command in agent-driven development runs.

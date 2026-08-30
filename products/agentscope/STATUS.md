# AgentScope status

## Product shape

AgentScope v0.9.0 is a zero-runtime-dependency Python CLI for explaining the
instruction files that apply to a repository target. Its `agents-md` profile
models nearest-file precedence. Its `copilot-cli` profile uses explicit,
repository-contained session and additional-directory inputs to discover
standard and modular instructions, diagnose malformed sources and references,
and explain resolved-path and normalized-content deduplication. Human and
versioned JSON output support missing-instructions, invalid-reference,
invalid-source, and profile-divergence gates.

## Completed on 2026-08-29

- Added root portfolio CI across every stable supported Python minor from 3.10
  through 3.14, with warning-strict tests at the oldest compatibility boundary.
- Added a reusable local validation entry point that runs AgentScope's 34 tests,
  compiles its source, builds its wheel, installs that wheel into a fresh
  environment, and exercises the installed `agentscope --version` command.
- Applied the same checks to frozen ProofRun without resuming its feature scope.
- Kept build, bytecode, wheel, and environment output outside the checkout and
  removed it after validation.
- Provisioned the shared declared `setuptools>=68` backend explicitly in CI and
  made local backend absence a concise validator preflight.
- Used read-only GitHub permissions, disabled retained checkout credentials, and
  pinned the current official checkout/setup action majors.
- Documented exact local use, build prerequisites, and the Ubuntu-only hosted
  matrix boundary.

## Changes since the prior run

AgentScope now has continuous compatibility and distribution-shape validation
instead of relying only on autonomous local runs. The workflow tests all
declared stable Python minors and proves the installed console command from a
built wheel. AgentScope behavior and schemas remain unchanged; ProofRun remains
frozen.

## Known issues

- User-home locations, `COPILOT_HOME`, implicit environment loading, interactive
  source disabling, and nested `AGENTS.md` interpretation inside an additional
  directory remain out of scope.
- GitHub documents additional directory source shapes but not precedence or
  nested `AGENTS.md` scope; AgentScope's direct-file and post-repository order is
  an explicit deterministic product contract.
- Unreadable or non-UTF-8 standard files cannot be content-compared and retain
  applied-source behavior; unreadable modular files are invalid.
- Content normalization deliberately ignores line placement, blank lines, and
  surrounding line whitespace only; it does not attempt Markdown semantics.
- A target above the session directory does not reclassify session-intermediate
  directories as target-nested modular locations.
- The frontmatter parser supports only a scalar, comma-separated `applyTo` and
  does not interpret `excludeAgent`, lists, mappings, or multiline values.
- Character classes, brace expansion, and glob negation are not modeled.
- AgentScope does not reproduce Copilot CLI's unpublished import size guard;
  the local 10-edge depth limit is intentionally product-defined.
- GitHub's Copilot CLI documentation does not explicitly demonstrate `?`;
  AgentScope documents conventional single-character behavior as its contract.
- Root hosted CI runs on Ubuntu only; Windows and macOS are not separate matrix
  dimensions.

## Decisions

- Stay read-only and dependency-free for the first useful experience.
- Use named client profiles rather than a misleading universal scope model.
- Keep session and additional-directory state explicit, repository-contained,
  deduplicated, and independent of process environment state.
- Model only a direct `AGENTS.md` plus recursive `*.instructions.md` beneath an
  additional directory; do not infer undocumented nested-agent scope.
- Report repository/session discovery first, then additional directories in
  caller order, without claiming client precedence.
- Deduplicate resolved paths first; compare normalized complete text among
  eligible standard and additional `AGENTS.md` sources, retaining the first.
- Reject any discovered instruction symlink that escapes the selected root.
- Use inspection schema v5 and comparison schema v3 to record the new effective
  input while preserving target and source objects.
- Keep portfolio validation in one root script, cover Python 3.10-3.14, promote
  warnings to errors on 3.10, and install wheels only in temporary environments.

## Recommended next step

Treat unreadable or non-UTF-8 standard Copilot instructions as explicit invalid
sources and cover their policy, output, comparison, and reference-expansion
behavior.

# Next-product opportunity comparison — 2026-08-20

This comparison follows the portfolio pivot decision and uses current product
documentation plus visible open-source alternatives. The goal was a frequent,
specific workflow with a useful local prototype that needs no account or secret.

## Candidate 1: instruction-scope debugger — selected

- **Target user:** maintainers using more than one coding-agent client or more
  than one nested instruction file.
- **Painful job:** answer which instructions apply to a proposed file before an
  agent starts work, and explain why a rule was combined, shadowed, or ignored.
- **Why now:** the open `AGENTS.md` format reports adoption by more than 60,000
  repositories and defines nearest-file precedence, while GitHub Copilot now
  supports repository, path-specific, AGENTS.md, CLAUDE.md, and GEMINI.md
  instructions across surfaces. Its CLI documentation says applicable files are
  combined without a general precedence order and explicitly warns authors to
  avoid conflicts.
- **Alternatives:** `agentslint` checks stale references and command targets;
  `agents-md-kit` lints content and schemas; readiness scanners score repository
  setup. These are useful complements but do not primarily simulate effective
  per-target scope for multiple client profiles.
- **Smallest useful wedge:** a read-only CLI that accepts target paths, models
  the portable nearest-`AGENTS.md` rule and Copilot CLI aggregation, reports
  matching path-specific instructions, and emits stable JSON for CI.
- **Distribution path:** `uvx`/pip, pre-commit, CI, and a future editor action.
- **Principal risk:** client behavior changes and glob semantics differ; every
  profile must be explicitly versioned and grounded in source documentation.

## Candidate 2: MCP configuration change reviewer

- **Target user:** developers reviewing shared MCP client configuration.
- **Painful job:** detect a proposed change that adds hard-coded secrets,
  untrusted local code execution, unencrypted remote endpoints, or weaker
  sandboxing before the server starts.
- **Why now:** VS Code warns that local MCP servers can execute arbitrary code,
  recommends input variables instead of hard-coded secrets, and now exposes
  explicit local server sandbox controls. The MCP specification likewise treats
  tools as arbitrary code execution and calls for consent and data controls.
- **Alternatives:** `mcp-scan`, `mcp-audit`, `mcpscan`, and other active scanners
  already cover configuration discovery, tool poisoning, baselines, SARIF, and
  runtime inspection.
- **Smallest useful wedge:** compare base and proposed JSON and explain only the
  security posture that worsened.
- **Distribution path:** pre-commit and pull-request checks.
- **Principal risk:** a crowded category makes a static heuristic MVP difficult
  to differentiate, while client-specific schemas change quickly.

## Candidate 3: coding-agent environment preflight

- **Target user:** maintainers delegating work to ephemeral cloud coding agents.
- **Painful job:** prove that documented setup and validation commands work in a
  clean checkout before paid agent time is spent.
- **Why now:** GitHub documents dedicated setup-step workflows for preinstalling
  dependencies in ephemeral agent environments and recommends keeping repository
  instructions current with build, lint, and test commands.
- **Alternatives:** dev containers, CI, repository-readiness scanners, and each
  agent vendor's environment configuration already cover much of the space.
- **Smallest useful wedge:** parse documented commands and run a non-mutating
  clean-worktree preflight with a diagnostic report.
- **Distribution path:** CI and a scheduled repository health check.
- **Principal risk:** safely executing arbitrary setup is materially more complex
  than inspecting it, and overlaps heavily with existing CI.

## Decision

AgentScope wins on specificity, differentiation, and prototype credibility. It
turns a documented cross-client ambiguity into a deterministic inspection step;
it is read-only, credential-free, and testable with disposable repositories.
The first release intentionally models only two named profiles instead of
claiming universal compatibility.

## Sources inspected

- [AGENTS.md open format](https://agents.md/) — adoption and nearest-file scope.
- [GitHub Copilot CLI custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions) — supported files, discovery, combination, and path references.
- [GitHub instruction support matrix](https://docs.github.com/en/copilot/reference/custom-instructions-support) — differing support across clients and surfaces.
- [GitHub Copilot environment setup](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment) — ephemeral environment and setup-step workflow.
- [VS Code MCP server configuration](https://code.visualstudio.com/docs/agent-customization/mcp-servers) — arbitrary-code warning, secret handling, and sandbox controls.
- [MCP specification security principles](https://modelcontextprotocol.io/specification/2025-03-26/index#security-and-trust--safety) — consent, privacy, and tool-safety requirements.
- [agentslint](https://github.com/jyablonski/agentslint), [agents-md-kit](https://github.com/reaatech/agents-md-kit), and [mcp-scan](https://github.com/mansilladev/mcp-scan) — adjacent open-source alternatives.

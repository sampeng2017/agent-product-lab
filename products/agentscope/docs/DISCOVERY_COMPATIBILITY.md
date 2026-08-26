# Copilot CLI repository discovery compatibility

This document records the repository-scoped discovery contract modeled by
AgentScope's `copilot-cli` profile as of 2026-08-25.

GitHub's current [Copilot CLI custom-instructions
documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)
defines standard locations as the repository root, the session working
directory, directories between them, and directories nested in the path of a
file being worked on. It lists `.github/copilot-instructions.md`, `AGENTS.md`,
`CLAUDE.md`, and `GEMINI.md` in those locations, adds
`.claude/CLAUDE.md` explicitly, and describes
`.github/instructions/**/*.instructions.md` as path-specific discovery. GitHub
also says applicable sources are combined, duplicate copies are removed, and
no general precedence order is defined.

## AgentScope behavior

AgentScope evaluates named targets rather than a live Copilot session, so the
repository root and every directory from it through the target's parent are its
standard-location chain. A planned target that does not exist uses its planned
parent directory.

For deterministic presentation, AgentScope visits that chain root-to-target.
Within each directory it checks these locations in order:

1. `.github/copilot-instructions.md`
2. `AGENTS.md`
3. `CLAUDE.md`
4. `.claude/CLAUDE.md`
5. `GEMINI.md`

After standard files, it visits each ancestor's
`.github/instructions/**/*.instructions.md` files root-to-target and sorts each
tree by repository-relative path. This order is an AgentScope reporting
contract, not a claim of Copilot precedence.

Supported `@` references still appear immediately after their parent in
depth-first order. Every directly discovered or referenced file is keyed by its
resolved path and reported once; the first discovery route wins. This prevents
a file imported by an earlier source from appearing again when a later standard
or modular route reaches it, including equivalent symlink routes.

## Deliberate boundary

AgentScope does not yet accept a separate Copilot session working directory.
Consequently, it cannot distinguish directories between that session directory
and the repository root from directories nested toward the target; it models
the target-ancestor chain consistently instead. User-level locations,
`COPILOT_HOME`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, disabled files from the
interactive `/instructions` command, and content-based duplicate detection are
also outside v0.6.0.

The existing source object shapes and policy exits are unchanged. Inspection
remains schema v3 and comparison remains schema v1.

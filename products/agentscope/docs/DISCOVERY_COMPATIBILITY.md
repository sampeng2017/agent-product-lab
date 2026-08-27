# Copilot CLI repository discovery compatibility

This document records the repository-scoped discovery contract modeled by
AgentScope's `copilot-cli` profile as of 2026-08-26.

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

AgentScope evaluates named targets rather than a live Copilot session. The
optional `--cwd` argument supplies the session working directory explicitly,
relative to `--root`; it defaults to `.`. AgentScope does not read the process
working directory as hidden profile state and does not change it. The session
directory must already exist, resolve inside the repository, and remain inside
it through symlinks. A planned target may be absent and uses its planned parent
directory.

For deterministic presentation, AgentScope visits standard locations in role
order: repository root, directories between the root and session, the session
directory, then target-path directories not already visited. A divergent
session and target branch therefore reports the session branch before the
target branch. Within each directory it checks these locations in order:

1. `.github/copilot-instructions.md`
2. `AGENTS.md`
3. `CLAUDE.md`
4. `.claude/CLAUDE.md`
5. `GEMINI.md`

After standard files, it visits modular
`.github/instructions/**/*.instructions.md` trees at the repository root, the
session directory, and target-nested directories. It deliberately skips
session-intermediate-only directories, matching GitHub's documented exception.
When the session is the repository root, this is the v0.6.0 root-to-target
behavior. For divergent branches, target-only locations follow the session
location. Each tree is sorted by repository-relative path. This order is an
AgentScope reporting contract, not a claim of Copilot precedence.

Supported `@` references still appear immediately after their parent in
depth-first order. Every directly discovered or referenced file is keyed by its
resolved path and reported once; the first discovery route wins. This prevents
a file imported by an earlier source from appearing again when a later standard
or modular route reaches it, including equivalent symlink routes.

## Output and deliberate boundary

Standard-source reasons name whether a file came from the repository root,
session intermediate, session directory, or target-nested location. Human
output also names the session directory. Inspection schema v4 and comparison
schema v2 add the repository-relative `session_directory`; their existing
target and source objects and policy exits are unchanged.

User-level locations, `COPILOT_HOME`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, files
disabled with interactive `/instructions`, and identical-content duplicate
detection remain outside v0.7.0. Resolved-file identity deduplication still
prevents the same file from appearing twice through direct, referenced, or
symlink-equivalent routes.

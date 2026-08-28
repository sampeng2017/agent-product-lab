# Copilot CLI repository discovery compatibility

This document records the repository-scoped discovery contract modeled by
AgentScope's `copilot-cli` profile as of 2026-08-28.

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

Eligible standard files also participate in content-copy detection:
`.github/copilot-instructions.md`, `AGENTS.md`, both `CLAUDE.md` locations, and
`GEMINI.md`. AgentScope normalizes each complete UTF-8 file by removing blank
lines, trimming surrounding whitespace on nonblank lines, and joining those
lines with single spaces. It does not perform partial-content or semantic
similarity matching. The first standard source with a normalized value remains
`applied`; later distinct paths with that value are reported as `duplicate`,
with a reason naming the first source. This map spans source kinds and all
repository, intermediate, session, target-nested, and divergent-branch roles.

Modular `*.instructions.md` and imported files neither participate in nor seed
standard-copy detection. References found in a duplicate standard source are
still resolved immediately relative to that copy. This conservative choice
keeps a repeated wrapper from hiding different files reached by the same
relative import. A reference already reached by resolved identity retains the
existing first-route-wins behavior.

## Output and deliberate boundary

Standard-source reasons name whether a file came from the repository root,
session intermediate, session directory, or target-nested location. Duplicate
reasons instead name the first retained source and state that relative imports
are still evaluated. Human output renders `DUPLICATE`; inspection schema v4
uses `state: "duplicate"` in the unchanged source object. Comparison schema v2
continues to compare applied paths only, so duplicates do not create profile
divergence. Policy exits are unchanged.

User-level locations, `COPILOT_HOME`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`, and
files disabled with interactive `/instructions` remain outside v0.8.0.
Unreadable or non-UTF-8 standard files cannot be content-compared and preserve
the prior applied-source behavior. Resolved-file identity deduplication still
prevents the same file from appearing twice through direct, referenced, or
symlink-equivalent routes.

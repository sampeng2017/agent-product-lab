# Copilot CLI repository discovery compatibility

This document records the repository-scoped discovery contract modeled by
AgentScope's `copilot-cli` profile as of 2026-09-05.

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

The same page documents comma-separated directories in
`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` as contributing additional `AGENTS.md` and
`*.instructions.md` files. It does not define precedence for those directories
or say that other standard names are loaded from them. AgentScope therefore
models only those two documented source shapes and exposes the list as explicit
CLI input instead of importing process environment state.

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

### Explicit additional directories

`--instructions-dir PATH` may be repeated for inspection and comparison.
Relative values are anchored at the selected repository root. Every value must
exist as a directory and remain inside that root after symlink resolution;
repeated or symlink-equivalent values retain their first position and appear
once in output. AgentScope never reads `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`
implicitly.

After ordinary standard and modular discovery, AgentScope visits each explicit
directory in caller order. It checks the directory's direct `AGENTS.md`, then
recursively discovers `*.instructions.md` files in repository-relative path
order. The direct-file boundary avoids claiming undocumented nested
`AGENTS.md` scoping, while recursive modular discovery follows the documented
file shape. This is an AgentScope reporting contract, not a precedence claim.

Additional `AGENTS.md` files expand supported relative references and
participate in normalized standard-content copy detection. Additional modular
files use the same repository-relative `applyTo` matching and diagnostics as
ordinary modular sources. Both categories share resolved-file identity with
all earlier routes, so pointing at an ordinary location does not duplicate it.
Source symlinks that resolve outside the repository are reported as invalid
instead of being read. Planned targets use their requested repository-relative
path exactly as ordinary modular matching does.

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
are still evaluated. Human output renders `DUPLICATE`; inspection schema v5
uses `state: "duplicate"` in the unchanged source object. Comparison schema v5
continues to calculate divergence from applied paths only, so duplicate,
ignored, shadowed, and invalid sources do not create profile divergence. It
separately retains each profile's ordered non-applied evidence and invalid
diagnostics with counts. The comparison's narrow
`--fail-on-invalid-references` or broad `--fail-on-invalid-sources` gate can
enforce invalid evidence. The separate `--fail-on-ignored-sources` gate rejects
only `ignored` path-instruction occurrences; `duplicate` and `shadowed` evidence
remains informational. Both document types record the effective, deduplicated
additional-directory list. The gate does not change schema v5 because the
triggering source state was already represented in both document types.

User-home locations, `COPILOT_HOME`, implicit environment loading, nested
`AGENTS.md` interpretation inside an additional directory, and files disabled
with interactive `/instructions` remain outside v0.15.0. A discovered Copilot
source must be readable UTF-8 before it can be applied or content-compared.
Decode failures use `instruction file is not valid UTF-8`; other read failures
use `instruction file could not be read`. Both are stable `invalid` diagnostics,
and exception details or file content are never included. Apparent references
inside unreadable content are not expanded. Resolved-file identity
deduplication still prevents the same file from appearing twice through direct,
referenced, additional-directory, or symlink-equivalent routes.

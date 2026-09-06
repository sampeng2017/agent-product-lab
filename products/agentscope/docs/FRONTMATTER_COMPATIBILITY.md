# Path-instruction frontmatter compatibility

This document records the deliberately small frontmatter contract modeled by
AgentScope's `copilot-cli` profile as of 2026-09-02.

GitHub's current [Copilot CLI custom-instructions
documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)
requires a frontmatter block at the start of every `*.instructions.md` file and
shows `applyTo` as a quoted, one-line glob scalar. Multiple patterns are placed
in that same scalar and separated with commas. GitHub also documents
`excludeAgent` as an optional sibling key. It does not document `applyTo` list,
mapping, or multiline forms.

AgentScope checks this narrow contract directly and does not attempt to parse
general YAML. This keeps the package dependency-free while distinguishing a
broken source from a valid source whose glob simply does not match the target.

## Outcomes

| Input | AgentScope outcome |
| --- | --- |
| opening `---`, one non-empty scalar `applyTo`, closing `---` | `applied` or `ignored`, depending on the glob match |
| multiple comma-separated scalar patterns | `applied` when any pattern matches |
| optional sibling keys such as `excludeAgent` | accepted but otherwise not interpreted |
| no opening `---` at the start of the file | `invalid`: opening delimiter required |
| no closing `---` | `invalid`: closing delimiter missing |
| no `applyTo` key | `invalid`: key missing |
| empty quoted or unquoted `applyTo` | `invalid`: scalar empty |
| block or inline YAML list | `invalid`: lists unsupported |
| mapping or multiline value | `invalid`: form unsupported |
| duplicate `applyTo`, missing colon, unmatched quote, or empty comma item | `invalid`: precise syntax diagnostic |
| file cannot be decoded as UTF-8 | `invalid`: stable encoding diagnostic |
| other file read failure | `invalid`: stable read diagnostic |
| readable scalar whose globs do not match | `ignored`, not invalid |

All path-instruction diagnostics use the existing `copilot-path` source kind
and `invalid` state, preserving the source object shape. They contribute to
`invalid_source_count` but not the narrower `invalid_reference_count`.

## Policy and output

Inspection remains informational by default. `--fail-on-invalid-sources` exits
1 after rendering the full report when any target has an invalid source,
including a malformed path instruction or an invalid `@` reference. The older
`--fail-on-invalid-references` keeps its exact narrower behavior. Both policies
can be combined with `--require-instructions` using OR semantics. The separate
`--fail-on-ignored-sources` gate exits 1 for a readable, valid path instruction
whose `applyTo` scalar does not match a requested target; it does not reject
duplicates, shadowed ancestors, malformed sources, or missing guidance by
itself. Invalid repository arguments still exit 2.

Inspection JSON schema v5 retains `invalid_source_count` at the document and
target levels. The existing `invalid_reference_count` remains and is always a
subset of that broader total. Source objects are unchanged; v5 adds the
effective additional-directory input documented by the discovery contract.
Comparison JSON schema v4 keeps applied-path divergence separate while adding
ordered invalid diagnostics and counts for every profile. Its
`--fail-on-invalid-sources` gate rejects malformed path instructions after
rendering the full comparison report, while
`--fail-on-invalid-references` deliberately does not reject them.

## Deliberate boundary

AgentScope does not claim to validate arbitrary YAML, interpret `excludeAgent`,
or infer undocumented Copilot behavior for alternate `applyTo` value types.
Unsupported forms are rejected explicitly instead of being guessed into a glob.

# Why an instruction rule misses its intended file

An API instruction file exists, but its `applyTo` pattern points at `web/`.
AgentScope discovers the file and reports it as `IGNORED` for `api/app.py`.
Repository-wide instructions still apply, so the target has guidance even
though the API-specific rule misses it.

This example shows how to locate that mismatch, make it a policy failure,
correct the pattern, and confirm that it covers the intended target.

## Replay the example

[Install AgentScope](../../docs/INSTALLATION.md#agentscope-100) and keep that
Python environment active. You need a current lab checkout for these example
files. From the lab root:

```sh
python examples/agentscope-rule-scope/demo.py
```

If you installed through pip and do not have a checkout:

```sh
git clone https://github.com/sampeng2017/agent-product-lab.git
cd agent-product-lab
python examples/agentscope-rule-scope/demo.py
```

The example is on current `main`, while the pinned installation revision
predates it. Cloning the example does not change the installed AgentScope
version. The script copies the fixture to a temporary directory and changes
only that copy. It checks the human command exits, JSON inspection and coverage
states, and file fingerprints before and after every inspection.

Successful replay exits 0, including the expected policy failure in its first
stage. Missing installed AgentScope exits 2 with an installation hint. Unexpected
results exit 1. Replays start from a fresh copy and remove it afterward.

## Find the missed rule

The commands below run automatically inside the replay's temporary project.
For manual inspection of the checked-in fixture, start from the lab root and
change directory first:

```sh
cd examples/agentscope-rule-scope/project
```

Use the replay to try the pattern correction without editing that checked-in
fixture.

The fixture's [.github/instructions/api.instructions.md](project/.github/instructions/api.instructions.md)
contains:

```markdown
---
applyTo: "web/**/*.py"
---
Validate API request inputs before processing them.
```

Inspect the intended target with the explicit profile that supports these
modular instruction files:

```sh
agentscope --profile copilot-cli --root . api/app.py
```

The relevant output is:

```text
api/app.py: 1 applied, 0 invalid, 0 invalid references
  IGNORED  .github/instructions/api.instructions.md [copilot-path] — applyTo does not match api/app.py
Exit: 0
```

The file was found and its pattern is valid. `IGNORED` explains that the
pattern did not select the target. The one applied source is the separate
repository-wide `.github/copilot-instructions.md`. Inspection is informational
by default, so exit 0 does not mean every discovered rule matched.

## Make the mismatch actionable

For this target, we expect the API rule to apply. Ask for a policy failure if
a discovered path rule is ignored:

```sh
agentscope --profile copilot-cli --root . --fail-on-ignored-sources api/app.py
```

The same explanation is printed, but the command now exits 1. This flag checks
all discovered path rules for the requested targets. Use it where those rules
are expected to match; intentional nonmatching rules also trigger it.

The coverage view shows which of the two files the rule actually selects:

```sh
agentscope coverage --compact --root . api/app.py web/app.py
```

Before correction, its matrix is:

```text
RULE | 1 | 2
-----+---+---
R1   | I | M
```

Here column 1 is `api/app.py`, column 2 is `web/app.py`, and `R1` is the API
instruction file. `I` means ignored and `M` means matched. Full legends are
printed with the actual matrix.

## Correct the scope

Change just the frontmatter pattern to:

```markdown
applyTo: "api/**/*.py"
```

The replay makes this edit in its temporary copy. Repeat the same target gate:

```text
api/app.py: 2 applied, 0 invalid, 0 invalid references
  APPLIED  .github/instructions/api.instructions.md [copilot-path] — applyTo matches api/app.py
Exit: 0
```

Coverage now shows `M | I`: the API file is matched and the web file is ignored.
That ignored web result is intentional. The strict target gate checks only
`api/app.py`; the two-target coverage command remains informational.

The final line is:

```text
PASS: ignored API rule -> corrected scope; inspections left files unchanged.
```

## Use the pattern in your project

Name the real target, inspect with `--profile copilot-cli`, read the discovered
source and its match reason, and check the source's frontmatter pattern. Use
coverage to compare representative intended and unintended targets after a
change. Review the full report before enforcing an ignored-source gate.

This example uses AgentScope's modeled `copilot-cli` profile. Its supported
scalar frontmatter and path globs are defined in the product's
[frontmatter](../../products/agentscope/docs/FRONTMATTER_COMPATIBILITY.md) and
[glob](../../products/agentscope/docs/GLOB_COMPATIBILITY.md) contracts. Actual
client discovery can depend on session and additional-directory settings;
see the [AgentScope README](../../products/agentscope/README.md).

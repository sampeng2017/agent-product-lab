# Try ProofRun on your own project

Does yesterday's passing test result still cover the code in front of you?
ProofRun records a check against Git state and tells you when that evidence
stops applying. This trial asks whether that distinction helps your real work.
It does not ask you to replace your test runner or CI.

Set a **ten-minute budget**, including installation and setup. That is a trial
limit, not a claim about setup speed. Stop and report where you got stuck if
the tool takes longer. No lab checkout is needed.

## Before you run anything

- Choose an existing Git project and a test/check command you already trust.
- Use the [pinned installation guide](INSTALLATION.md#proofrun-181).
  The [pipx route](INSTALLATION.md#install-cli-apps-with-pipx) keeps the tool
  outside your project; it does not supply project test dependencies.
- Activate your project's test environment if its command uses `python`,
  `pytest`, or another executable on PATH. Review any command before running it.
- Note your current workflow and start time. Keep private repository names,
  source code, credentials, and local paths out of public feedback.

## 1. Preview one check

From your project's root, review existing changes; do not reset or clean them:

If `proofrun.toml` already exists, **do not overwrite it**. Skip initialization
and substitute an existing check name for `trial` in step 2 onward. Do not use
`--force` just to complete this trial.

```sh
git status --short
proofrun init --dry-run --check-name trial
```

Read the proposed command. Confirm it selects the tests you intend to run,
not an empty or unrelated suite. The preview creates no files or receipts.
If detection fails, give your actual command explicitly. For a project whose
tests use unittest, for example:

```sh
proofrun init --dry-run --check-name trial -- python -B -m unittest discover -s tests -v
```

## 2. Record your first useful result

For a **new configuration only**, repeat your reviewed initialization without
`--dry-run`. For the detected route:

```sh
proofrun init --check-name trial
```

For an explicit command, keep that same command when creating the manifest.
Then run your named check (or the existing check you selected):

```sh
proofrun verify trial
proofrun status --require-valid trial
proofrun audit
```

Initialization creates `proofrun.toml`; verification runs your command and
creates the default ignored `.proofrun/` evidence directory. It does not commit
your files. Your verification command can itself write files or have other
effects, so review it first.

Record elapsed minutes to your first `VALID`, or to the point where you stopped.
Existing uncommitted changes are allowed: evidence covers that current state.
`VALID` does not establish test completeness, code correctness, or a signature.
If tests fail or proof is rejected, use the
[recovery guide](PROOFRUN_TROUBLESHOOTING.md); a blocked result is useful feedback.

## 3. Check evidence after your next normal edit

Do not create a fake bug or discard real work for the trial. After an ordinary
source edit in this project, ask whether the earlier evidence still applies:

```sh
proofrun status --require-valid trial
```

`STALE` and exit 1 are expected after a Git-visible edit. Status did not run your
tests. Review the change and run fresh verification when appropriate:

```sh
proofrun verify trial
proofrun status --require-valid trial
```

Ignored-file changes and edits fully restored before a check finishes are
outside this Git-state boundary. Audit checks receipt consistency, not whether
old proof is current. Keep these limits in mind when deciding whether it helps.

## 4. Tell us what actually happened

[Open the voluntary first-use feedback form](https://github.com/sampeng2017/agent-product-lab/issues/new?template=proofrun-first-use.yml).
It opens a draft; nothing is submitted automatically. Posting requires a GitHub
account, and submitted issues are public. Do not attach receipt stores, full
reports, private commands, or environment values. A short redacted description
is enough. You can also keep the notes locally without posting.

Tell us your existing workflow, result or blocker, elapsed time, and whether
ProofRun added value or just steps. **“I would rather use my existing workflow”
is a useful answer.** This trial adds no telemetry or automatic reporting.

If you use ProofRun again during a later real task, update the same issue with
the task and result. Finishing this guide or repeating its demonstration is not
repeat-use evidence. Intent to return is not the same as returning.

Prefer a disposable demonstration before trying your project? Use the existing
[stale-proof replay](../examples/proofrun-stale-proof/README.md), which changes
only a temporary copy. That checks the mechanics; it does not validate demand.

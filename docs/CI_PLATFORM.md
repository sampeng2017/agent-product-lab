# Hosted CI platform policy

Portfolio CI uses `ubuntu-24.04` and explicitly selects Python 3.10–3.14 with
`actions/setup-python`. This preserves the OS baseline of the green hosted matrix.

GitHub [announced](https://github.com/actions/runner-images/issues/14748) that
`ubuntu-latest` will move to Ubuntu 26.04 between October 19 and November 19,
2026. An explicit supported label prevents that alias migration from changing
the release environment without a repository decision.

The label selects an OS series, not an immutable image. GitHub still updates
the image and software. Python patches, build dependencies, and action majors
can also evolve. Set up job logs record the actual OS and image version.

## Review and upgrade

Review at the next platform-related release, a label-deprecation announcement,
or by November 5, 2026, whichever comes first. Check the current
[supported-image list](https://github.com/actions/runner-images#available-images).

Before upgrading, run the same validator on the proposed image across Python
3.10–3.14. Investigate build, install, process, Git, and artifact differences.
Change the baseline only after a green trial; retain the supported old label
and document the cause if the trial fails.

```sh
PYTHON_BIN=python3.11 PYTHONWARNINGS=error ./scripts/validate-portfolio.sh
```

Local validation tests the active host; hosted runs prove the configured CI
platform. This policy covers the root workflow. Product-specific examples and
generated workflows keep their own documented behavior.

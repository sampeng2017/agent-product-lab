# Hosted CI platform policy

Portfolio CI uses `ubuntu-24.04` and explicitly selects Python 3.10–3.15 with
`actions/setup-python`. This preserves the OS baseline of the green hosted matrix.

GitHub [announced](https://github.com/actions/runner-images/issues/14748) that
`ubuntu-latest` will move to Ubuntu 26.04 between October 19 and November 19,
2026. An explicit supported label prevents that alias migration from changing
the release environment without a repository decision.

The label selects an OS series, not an immutable image. GitHub still updates
the image and software. Python patches, build dependencies, and action majors
can also evolve. Set up job logs record the actual OS and image version.

## Interpreter coverage and lifecycle

Python 3.15.0 became stable on October 9, 2026. The October 14
[six-job trial](https://github.com/sampeng2017/agent-product-lab/actions/runs/38585956760)
passed the full validator, including the new 3.15 job's tests, reproducible
builds, isolated installs, behavior/release contracts, and artifact integrity.
The product runtime and build definitions still match the published install pins.
No version, dependency, source pin, or OS-series change was required.

As of October 14, Python.org lists 3.11–3.15 as maintained and 3.10 as
end-of-life. Prefer maintained interpreters for new environments. The 3.10
job remains a warning-strict compatibility-floor check; it does not extend
upstream security maintenance or imply a changed package minimum.
See the [Python lifecycle table](https://devguide.python.org/versions/) and
[3.15 release](https://www.python.org/downloads/release/python-3150/).

Review each new stable interpreter with the same full hosted validator before
extending public coverage claims. Coverage is for the tested regular CPython
builds on this OS; it does not establish free-threaded, prerelease, future
interpreter, alternate implementation, or Windows compatibility. The external
CI starter keeps its separate Python 3.11 choice.

## Review and upgrade

Review at the next platform-related release, a label-deprecation announcement,
or by November 5, 2026, whichever comes first. Check the current
[supported-image list](https://github.com/actions/runner-images#available-images).

Before upgrading, run the same validator on the proposed image across Python
3.10–3.15. Investigate build, install, process, Git, and artifact differences.
Change the baseline only after a green trial; retain the supported old label
and document the cause if the trial fails.

```sh
PYTHON_BIN=python3.11 PYTHONWARNINGS=error ./scripts/validate-portfolio.sh
```

Local validation tests the active host; hosted runs prove the configured CI
platform. This policy covers the root workflow. Product-specific examples and
generated workflows keep their own documented behavior.

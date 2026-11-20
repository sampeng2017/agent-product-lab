# Hosted CI platform policy

Portfolio CI uses `ubuntu-24.04` and explicitly selects Python 3.10–3.15 with
`actions/setup-python`. This preserves the OS baseline of the green hosted matrix.

GitHub [announced](https://github.com/actions/runner-images/issues/14748) an
`ubuntu-latest` migration to Ubuntu 26.04 with a target rollout window of
October 19–November 19, 2026. That schedule alone does not establish which image
a particular run receives. An explicit supported label prevents alias changes
from selecting a different OS series without a repository decision.

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

As reviewed November 19, Python.org lists 3.11–3.15 as maintained and 3.10 as
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
or by December 19, 2026, whichever comes first. Check the current
[supported-image list](https://github.com/actions/runner-images#available-images).

The prior November 5 checkpoint was overdue; the review below was performed
on November 19 and is not backdated.

Before upgrading, run the same validator on the proposed image across Python
3.10–3.15. Investigate build, install, process, Git, and artifact differences.
Change the baseline only after a green trial; retain the supported old label
and document the cause if the trial fails.

## November 19 review: retain the explicit baseline

Decision: keep `ubuntu-24.04` for root CI and the existing external starter.
The [reviewed upstream catalog](https://github.com/actions/runner-images/blob/fbb26cb01c3651ea3a0347e54bfa2ef83d740d49/README.md#available-images)
lists both `ubuntu-24.04` and `ubuntu-26.04`. It still associates `ubuntu-latest`
with 24.04 while the announcement targets 26.04. These public surfaces are not
proof of a completed global alias cutover; inspect each run's actual metadata.
No product need required an OS-series change, and no 26.04 trial or compatibility
claim is made by this review.

A fresh [six-job baseline run](https://github.com/sampeng2017/agent-product-lab/actions/runs/44671600749)
on unchanged source `dcf8dd6` passed the full portfolio validator. Setup logs
reported Ubuntu 24.04.5 for every job, with these observed tool/image versions:

| Python | Runner image version |
| --- | --- |
| 3.10.22 | 20261116.133.1 |
| 3.11.18 | 20261116.133.1 |
| 3.12.16 | 20261111.370.1 |
| 3.13.18 | 20261111.370.1 |
| 3.14.10 | 20261116.133.1 |
| 3.15.2 | 20261111.127.1 |

The three image revisions in one matrix demonstrate why the OS label is not
an immutable environment pin. This is a dated observation, not a promise that
future jobs use those revisions. The validator compares two wheel builds
within each job; it does not claim byte identity across different images or
interpreters. No workflow, interpreter list, product version, source install
pin, or required gate changed. Revisit by December 19 or an earlier review trigger.

```sh
PYTHON_BIN=python3.11 PYTHONWARNINGS=error ./scripts/validate-portfolio.sh
```

Local validation tests the active host; hosted runs prove the configured CI
platform. This policy covers the root workflow. Product-specific examples and
generated workflows keep their own documented behavior.

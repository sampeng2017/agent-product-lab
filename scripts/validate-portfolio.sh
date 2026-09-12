#!/bin/sh
set -eu

portfolio_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
portfolio_python=${PYTHON_BIN:-python3}
validation_python_warnings=${PYTHONWARNINGS:-default}
unset PYTHONWARNINGS
validation_temp=$(mktemp -d "${TMPDIR:-/tmp}/portfolio-validation.XXXXXX")
trap 'rm -rf "$validation_temp"' EXIT HUP INT TERM
export PIP_CACHE_DIR="$validation_temp/pip-cache"
export PIP_DISABLE_PIP_VERSION_CHECK=1

if ! "$portfolio_python" -c '
import setuptools.build_meta
from importlib.metadata import version
raise SystemExit(int(version("setuptools").split(".", 1)[0]) < 68)
' >/dev/null 2>&1; then
    echo "Portfolio validation requires setuptools>=68 for $portfolio_python." >&2
    echo "Install the declared pyproject build requirement or choose PYTHON_BIN." >&2
    exit 2
fi

validate_product() {
    product_name=$1
    console_command=$2
    smoke_argument=$3
    product_root="$portfolio_root/products/$product_name"
    wheel_dir="$validation_temp/wheels/$product_name"
    environment_dir="$validation_temp/environments/$product_name"
    pycache_dir="$validation_temp/pycache/$product_name"

    portfolio_version=$("$portfolio_python" --version 2>&1)
    echo "Validating $product_name with $portfolio_version"
    (
        cd "$product_root"
        PYTHONWARNINGS="$validation_python_warnings" \
            PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
            "$portfolio_python" -m unittest discover -s tests -v
        PYTHONWARNINGS="$validation_python_warnings" \
            PYTHONPYCACHEPREFIX="$pycache_dir" PYTHONPATH=src \
            "$portfolio_python" -m compileall -q src tests
    )

    mkdir -p "$wheel_dir"
    "$portfolio_python" -m pip wheel \
        --no-deps \
        --no-build-isolation \
        --wheel-dir "$wheel_dir" \
        "$product_root"
    "$portfolio_python" -m venv "$environment_dir"
    "$environment_dir/bin/python" -m pip install \
        --no-index \
        --no-deps \
        "$wheel_dir"/*.whl
    "$environment_dir/bin/$console_command" "$smoke_argument"
}

expect_policy_exit() {
    output_path=$1
    shift
    if "$@" >"$output_path"; then
        echo "Expected policy exit 1 from: $*" >&2
        return 1
    else
        policy_status=$?
    fi
    if [ "$policy_status" -ne 1 ]; then
        echo "Expected policy exit 1, got $policy_status from: $*" >&2
        return 1
    fi
}

validate_agentscope_distribution() {
    agentscope_command=$1
    fixture_root="$portfolio_root/products/agentscope/tests/fixtures/release-repository"
    audit_root="$validation_temp/agentscope-release-audit"
    mkdir -p "$audit_root"

    "$agentscope_command" --root "$fixture_root" src/app.py >/dev/null
    "$agentscope_command" compare --root "$fixture_root" src/app.py >/dev/null
    "$agentscope_command" coverage \
        --root "$fixture_root" docs/readme.md src/app.py >/dev/null

    expect_policy_exit "$audit_root/inspection.json" \
        "$agentscope_command" --profile copilot-cli --json \
        --fail-on-invalid-sources --root "$fixture_root" src/app.py
    expect_policy_exit "$audit_root/comparison.json" \
        "$agentscope_command" compare --json --fail-on-divergence \
        --root "$fixture_root" src/app.py
    expect_policy_exit "$audit_root/coverage.json" \
        "$agentscope_command" coverage --json --fail-on-ignored-sources \
        --fail-on-invalid-sources --root "$fixture_root" \
        docs/readme.md src/app.py

    "$portfolio_python" -c '
import json
import pathlib
import sys

inspection, comparison, coverage = (
    json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    for path in sys.argv[1:]
)
assert inspection["schema_version"] == 5
assert inspection["target_count"] == 1
assert inspection["invalid_source_count"] == 1
assert comparison["schema_version"] == 5
assert comparison["divergent_target_count"] == 1
assert comparison["invalid_source_count"] == 1
assert coverage["schema_version"] == 1
assert coverage["target_count"] == 2
assert coverage["matched_target_count"] == 1
assert coverage["ignored_target_count"] == 1
assert coverage["invalid_target_count"] == 2
' \
        "$audit_root/inspection.json" \
        "$audit_root/comparison.json" \
        "$audit_root/coverage.json"
    echo "AgentScope installed command surfaces and policy exits passed."
}

validate_product agentscope agentscope --version
validate_agentscope_distribution \
    "$validation_temp/environments/agentscope/bin/agentscope"
validate_product proofrun proofrun --help

echo "Portfolio validation passed; temporary build output was removed."

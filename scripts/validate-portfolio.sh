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

validate_product wheelcontract wheelcontract --version
validate_product agentscope agentscope --version
"$validation_temp/environments/wheelcontract/bin/wheelcontract" \
    --wheel "$validation_temp/wheels/agentscope"/*.whl \
    "$portfolio_root/wheelcontract.toml"
validate_product proofrun proofrun --help

echo "Portfolio validation passed; temporary build output was removed."

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
    build_source="$validation_temp/sources/$product_name"
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

    mkdir -p "$validation_temp/sources" "$wheel_dir"
    cp -R "$product_root" "$build_source"
    "$portfolio_python" -m pip wheel \
        --no-deps \
        --no-build-isolation \
        --wheel-dir "$wheel_dir" \
        "$build_source"
    "$portfolio_python" -m venv "$environment_dir"
    "$environment_dir/bin/python" -m pip install \
        --no-index \
        --no-deps \
        "$wheel_dir"/*.whl
    "$environment_dir/bin/$console_command" "$smoke_argument"
}

validate_product residuecheck residuecheck --version
residue_fixture="$validation_temp/residue-fixture"
mkdir -p "$residue_fixture"
printf '*.cache\n' > "$residue_fixture/.gitignore"
printf 'before\n' > "$residue_fixture/modified.cache"
printf 'before\n' > "$residue_fixture/removed.cache"
residue_output="$validation_temp/residue-output.txt"
if "$validation_temp/environments/residuecheck/bin/residuecheck" \
    --root "$residue_fixture" \
    -- "$portfolio_python" -c \
    "from pathlib import Path; Path('created.cache').write_text('new'); Path('modified.cache').write_text('after'); Path('removed.cache').unlink()" \
    > "$residue_output"; then
    echo "ResidueCheck fixture unexpectedly passed." >&2
    exit 1
else
    residue_exit=$?
fi
if [ "$residue_exit" -ne 1 ]; then
    echo "ResidueCheck fixture returned $residue_exit instead of 1." >&2
    exit 1
fi
"$portfolio_python" - "$residue_output" <<'PY'
from pathlib import Path
import sys

output = Path(sys.argv[1]).read_text(encoding="utf-8")
expected = (
    "CREATED created.cache",
    "MODIFIED modified.cache",
    "REMOVED removed.cache",
    "3 changes (1 created, 1 modified, 1 removed)",
)
missing = [fragment for fragment in expected if fragment not in output]
if missing:
    raise SystemExit(f"ResidueCheck installed fixture missing: {missing!r}")
PY
validate_product releasefact releasefact --version
"$validation_temp/environments/releasefact/bin/releasefact" \
    "$portfolio_root/releasefact.toml"
validate_product wheelcontract wheelcontract --version
"$validation_temp/environments/wheelcontract/bin/wheelcontract" \
    --wheel "$validation_temp/wheels/wheelcontract"/*.whl \
    "$portfolio_root/products/wheelcontract/wheelcontract.toml"
validate_product agentscope agentscope --version
"$validation_temp/environments/wheelcontract/bin/wheelcontract" \
    --wheel "$validation_temp/wheels/agentscope"/*.whl \
    "$portfolio_root/wheelcontract.toml"
validate_product proofrun proofrun --help

echo "Portfolio validation passed; temporary build output was removed."

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_DIR="${ROOT_DIR}/python"

"${ROOT_DIR}/scripts/check.sh"
"${ROOT_DIR}/scripts/build_python.sh"

TWINE_PYTHON="${PYTHON_BIN:-python3}"
if ! "${TWINE_PYTHON}" -m twine --version >/dev/null 2>&1; then
  TWINE_VENV="${TMPDIR:-/tmp}/bluearf-nova-publish-venv"
  "${PYTHON_BIN:-python3}" -m venv "${TWINE_VENV}"
  "${TWINE_VENV}/bin/python" -m pip install --quiet --upgrade pip twine
  TWINE_PYTHON="${TWINE_VENV}/bin/python"
fi

if [[ -n "${PYPI_API_TOKEN:-}" ]]; then
  export TWINE_USERNAME="__token__"
  export TWINE_PASSWORD="${PYPI_API_TOKEN}"
fi

if [[ -z "${TWINE_PASSWORD:-}" ]]; then
  printf 'Set PYPI_API_TOKEN or TWINE_PASSWORD before publishing.\n' >&2
  exit 2
fi

"${TWINE_PYTHON}" -m twine check "${PYTHON_DIR}/dist/"*
"${TWINE_PYTHON}" -m twine upload "${PYTHON_DIR}/dist/"*

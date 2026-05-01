#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_DIR="${ROOT_DIR}/python"

BUILD_PYTHON="${PYTHON_BIN:-python3}"
if ! "${BUILD_PYTHON}" -m build --version >/dev/null 2>&1; then
  BUILD_VENV="${TMPDIR:-/tmp}/bluearf-nova-build-venv"
  "${PYTHON_BIN:-python3}" -m venv "${BUILD_VENV}"
  "${BUILD_VENV}/bin/python" -m pip install --quiet --upgrade pip build
  BUILD_PYTHON="${BUILD_VENV}/bin/python"
fi

rm -rf "${PYTHON_DIR}/dist" "${PYTHON_DIR}/build" "${PYTHON_DIR}"/*.egg-info
(
  cd "${PYTHON_DIR}"
  "${BUILD_PYTHON}" -m build
)

printf 'Built package artifacts under %s/dist\n' "${PYTHON_DIR}"

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${1:-/tmp/bluearf-nova}"

rm -rf "${TARGET_DIR}"
mkdir -p "${TARGET_DIR}"

cp -R \
  "${ROOT_DIR}/.agents" \
  "${ROOT_DIR}/.github" \
  "${ROOT_DIR}/.gitignore" \
  "${ROOT_DIR}/LICENSE" \
  "${ROOT_DIR}/README.md" \
  "${ROOT_DIR}/plugins" \
  "${ROOT_DIR}/python" \
  "${ROOT_DIR}/scripts" \
  "${TARGET_DIR}/"

find "${TARGET_DIR}" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "${TARGET_DIR}" -name '*.pyc' -delete
find "${TARGET_DIR}" -name '.DS_Store' -delete

printf 'Exported standalone Bluearf Nova package to %s\n' "${TARGET_DIR}"
printf 'Next:\n'
printf '  cd %s\n' "${TARGET_DIR}"
printf '  git init && git add . && git commit -m \"Initial Bluearf Nova SDK and Codex plugin\"\n'
printf '  gh repo create bluearf/bluearf-nova-sdk --public --source . --push\n'

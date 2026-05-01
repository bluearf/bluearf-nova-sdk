#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_DIR="${ROOT_DIR}/python"

python3 -m py_compile \
  "${PYTHON_DIR}/bluearf_nova/client.py" \
  "${PYTHON_DIR}/bluearf_nova/cli.py"

PYTHONPATH="${PYTHON_DIR}" python3 -m bluearf_nova.cli --help >/dev/null
PYTHONPATH="${PYTHON_DIR}" python3 - <<'PY'
from bluearf_nova import BluearfNova, BluearfAPIError, __version__
assert BluearfNova
assert BluearfAPIError
assert __version__
PY

test -f "${ROOT_DIR}/plugins/bluearf-nova/.codex-plugin/plugin.json"
test -f "${ROOT_DIR}/plugins/bluearf-nova/skills/bluearf-nova/SKILL.md"
test -x "${ROOT_DIR}/plugins/bluearf-nova/scripts/bluearf-nova"

printf 'Bluearf Nova SDK and plugin checks passed.\n'


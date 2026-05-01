# Bluearf Nova SDK and Codex Plugin

This repository bundle contains two customer-facing integration surfaces for
Bluearf Nova:

- `python/`: publishable Python SDK and `bluearf` CLI package for PyPI.
- `plugins/bluearf-nova/`: Codex plugin package that guides Codex to use the
  Bluearf Nova SDK/CLI safely with customer API tokens.

The public API contract is versioned under:

```text
https://bluearf-nova-api-walbuhs3uq-uc.a.run.app/v1
```

API access is controlled with a Bluearf API Token:

```bash
export BLUEARF_NOVA_API_TOKEN="..."
```

## Quick Start

```bash
cd python
python3 -m pip install -e .
bluearf credits get
bluearf vehicles list --company-id COMPANY_ID --limit 25
```

## Codex Plugin

The plugin can be installed from this repository package by pointing Codex to:

```text
plugins/bluearf-nova
```

The plugin does not store tokens. Customers should provide tokens through
environment variables or their own secret management:

```bash
export BLUEARF_NOVA_API_TOKEN="..."
```

## Publishing

Local checks:

```bash
scripts/check.sh
```

Build Python package:

```bash
scripts/build_python.sh
```

Publish to PyPI:

```bash
PYPI_API_TOKEN="pypi-..." scripts/publish_pypi.sh
```

Export this folder as a standalone GitHub repo:

```bash
scripts/export_standalone_repo.sh /tmp/bluearf-nova
```

Then create/push the GitHub repo from `/tmp/bluearf-nova`.


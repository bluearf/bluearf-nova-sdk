# Bluearf Nova SDK and Codex Plugin

This repository bundle contains two customer-facing integration surfaces for
Bluearf Nova:

- `python/`: publishable Python SDK and `bluearf` CLI package for PyPI.
- `plugins/bluearf-nova/`: Codex plugin package that guides Codex to use the
  Bluearf Nova SDK/CLI safely with customer API tokens.

The public API contract is versioned under:

```text
https://api.bluearf.com/v1
```

API access is controlled with a Bluearf API key:

```bash
export BLUEARF_NOVA_API_KEY="..."
```

`BLUEARF_NOVA_API_TOKEN` is accepted for compatibility, but new integrations
should use `BLUEARF_NOVA_API_KEY`.

## Documentation

- Turkish guide: [`docs/tr/README.md`](docs/tr/README.md)
- English guide: [`docs/en/README.md`](docs/en/README.md)
- Python package guide: [`python/README.md`](python/README.md)
- Codex plugin guide: [`plugins/bluearf-nova/README.md`](plugins/bluearf-nova/README.md)

## Quick Start

```bash
cd python
python3 -m pip install -e .
export BLUEARF_NOVA_API_KEY="..."

bluearf credits get
bluearf companies list
bluearf uploads create --company-id COMPANY_ID --source binek_ticari_araclar --year 2024 --filename fleet.xlsx
bluearf nova-runs create --company-id COMPANY_ID --source binek_ticari_araclar --coid FACILITY_ID --year 2024 --file-id FILE_ID --auto-column-match --auto-enrich --auto-safe-save
bluearf nova-runs get --run-id RUN_ID
bluearf nova-runs questions --run-id RUN_ID --status pending
bluearf vehicles list --company-id COMPANY_ID --limit 25
bluearf calculations passenger-commercial-vehicles --company-id COMPANY_ID --coid COID --year 2024 --input examples/passenger_commercial_rows.en.json
```

The calculation command is a dry run. It returns a carbon preview and does not
create `carbonData`, `vehicleData`, or `CarbonDataUniform` records.

## Codex Plugin

The plugin can be installed from this repository package by pointing Codex to:

```text
plugins/bluearf-nova
```

The plugin does not store tokens. Customers should provide tokens through
environment variables or their own secret management:

```bash
export BLUEARF_NOVA_API_KEY="..."
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

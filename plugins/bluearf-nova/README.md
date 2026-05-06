# Bluearf Nova Codex Plugin

This plugin lets Codex use the Bluearf Nova Public API through the official
Python SDK and CLI.

It supports Turkish and English responses through `BLUEARF_NOVA_LANGUAGE` or
the global `--language tr|en` CLI flag.

## Install

Install or expose this plugin folder to Codex:

```text
plugins/bluearf-nova
```

Then set a customer API token:

```bash
export BLUEARF_NOVA_API_KEY="..."
```

The plugin uses `https://api.bluearf.com/v1` by default. Use
`BLUEARF_NOVA_API_URL` only for an explicit non-default environment.

`BLUEARF_NOVA_API_TOKEN` is still accepted for compatibility, but new customer
setups should use `BLUEARF_NOVA_API_KEY`.

## Check

```bash
plugins/bluearf-nova/scripts/check-bluearf-nova
```

## Example

```bash
plugins/bluearf-nova/scripts/bluearf-nova credits get
plugins/bluearf-nova/scripts/bluearf-nova companies list
plugins/bluearf-nova/scripts/bluearf-nova uploads create --company-id COMPANY_ID --source binek_ticari_araclar --year 2024 --filename fleet.xlsx
plugins/bluearf-nova/scripts/bluearf-nova nova-runs create --company-id COMPANY_ID --source binek_ticari_araclar --coid FACILITY_ID --year 2024 --file-id FILE_ID --auto-column-match --auto-enrich --auto-safe-save
plugins/bluearf-nova/scripts/bluearf-nova nova-runs get --run-id RUN_ID
plugins/bluearf-nova/scripts/bluearf-nova nova-runs questions --run-id RUN_ID --status pending
plugins/bluearf-nova/scripts/bluearf-nova vehicles list --company-id COMPANY_ID --limit 25
plugins/bluearf-nova/scripts/bluearf-nova calculations passenger-commercial-vehicles --company-id COMPANY_ID --coid COID --year 2024 --input examples/passenger_commercial_rows.en.json
```

`calculations passenger-commercial-vehicles` is dry-run and does not save
records. Nova Runs can save only when `--auto-safe-save` is enabled and the
backend finds no blockers.

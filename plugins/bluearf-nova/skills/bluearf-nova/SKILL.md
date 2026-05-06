---
name: bluearf-nova
description: Use when the user wants Codex to access the Bluearf Nova Public API through the official SDK or CLI, including Nova Runs AI pipelines, uploads, credits, usage, companies, vehicles, vehicle model references, carbon records, CarbonDataUniform, and passenger/commercial vehicle carbon calculations.
---

# Bluearf Nova

Use the Bluearf Nova Public API through the official Python SDK and CLI. This
plugin is customer-facing and must use Bluearf API keys, not internal session tokens.

## Required Token Handling

- Commands require `BLUEARF_NOVA_API_KEY`. `BLUEARF_NOVA_API_TOKEN` is accepted only for compatibility.
- Never print, log, commit, or invent tokens.
- If no token is set, ask the user to set `BLUEARF_NOVA_API_KEY` in their shell.
- Responses default to Turkish (`tr`). Use `--language en` for English responses or set `BLUEARF_NOVA_LANGUAGE=en`.
- The default public API base URL is `https://api.bluearf.com/v1`. Use `BLUEARF_NOVA_API_URL` only when the user explicitly needs a non-default API base URL.

## Preferred Command Wrapper

Prefer the plugin wrapper so Codex works both from source and after package
installation:

```bash
plugins/bluearf-nova/scripts/bluearf-nova --help
```

If the plugin is installed somewhere else, resolve the command relative to the
plugin root.

## Common Commands

```bash
plugins/bluearf-nova/scripts/bluearf-nova credits get
plugins/bluearf-nova/scripts/bluearf-nova usage list --days 7 --limit 25
plugins/bluearf-nova/scripts/bluearf-nova companies list
plugins/bluearf-nova/scripts/bluearf-nova uploads create --company-id COMPANY_ID --source binek_ticari_araclar --year 2024 --filename fleet.xlsx
plugins/bluearf-nova/scripts/bluearf-nova nova-runs create --company-id COMPANY_ID --source binek_ticari_araclar --coid FACILITY_ID --year 2024 --file-id FILE_ID --auto-column-match --auto-enrich --auto-safe-save
plugins/bluearf-nova/scripts/bluearf-nova nova-runs get --run-id RUN_ID
plugins/bluearf-nova/scripts/bluearf-nova nova-runs questions --run-id RUN_ID --status pending
plugins/bluearf-nova/scripts/bluearf-nova nova-runs answer-question --run-id RUN_ID --question-id QUESTION_ID --answer "Company Vehicle"
plugins/bluearf-nova/scripts/bluearf-nova nova-runs skip-question --run-id RUN_ID --remaining
plugins/bluearf-nova/scripts/bluearf-nova nova-runs export --run-id RUN_ID --limit 100
plugins/bluearf-nova/scripts/bluearf-nova vehicles list --company-id COMPANY_ID --limit 25
plugins/bluearf-nova/scripts/bluearf-nova vehicle-models search --brand Toyota --model Corolla --limit 10
plugins/bluearf-nova/scripts/bluearf-nova carbon-records list --company-id COMPANY_ID --year 2024
plugins/bluearf-nova/scripts/bluearf-nova carbon-uniform list --company-id COMPANY_ID --coid COID
plugins/bluearf-nova/scripts/bluearf-nova calculations passenger-commercial-vehicles --company-id COMPANY_ID --coid COID --year 2024 --input rows.json
```

`calculations passenger-commercial-vehicles` is dry-run and returns `carbonDataPreview` without saving records.
Nova Runs can save only when `--auto-safe-save` is enabled and the backend finds no blockers.

## SDK Usage

```python
import os
from bluearf_nova import BluearfNova

client = BluearfNova(api_key=os.environ["BLUEARF_NOVA_API_KEY"])
credits = client.credits.get()
companies = client.companies.list()
upload = client.uploads.create(company_id="COMPANY_ID", source="binek_ticari_araclar", year=2024, filename="fleet.xlsx")
run = client.nova_runs.create(company_id="COMPANY_ID", source="binek_ticari_araclar", coid="FACILITY_ID", year=2024, file_id=upload["data"]["file_id"])
vehicles = client.vehicles.list(company_id="COMPANY_ID", limit=25)
```

## Guardrails

- Keep responses concise and summarize large JSON payloads.
- Respect API errors and quota messages; do not retry blindly on insufficient credits.
- For data queries, preserve `company_id`, `organization_id`, `source`, `year`, and `coid` filters exactly as requested.
- Do not use this plugin for internal Firestore writes, Nova backend deploys, or private session auth.
- API token creation uses the Nova management backend and requires a real Nova management JWT via `BLUEARF_NOVA_MANAGEMENT_TOKEN` or `--management-token`. The SDK does not perform token exchange and does not include third-party Web API keys.

---
name: bluearf-nova
description: Use when the user wants Codex to access the Bluearf Nova Public API through the official SDK or CLI, including credits, usage, companies, vehicles, vehicle model references, carbon records, CarbonDataUniform, and passenger/commercial vehicle carbon calculations.
---

# Bluearf Nova

Use the Bluearf Nova Public API through the official Python SDK and CLI. This
plugin is customer-facing and must use Bluearf API Tokens, not Firebase tokens.

## Required Token Handling

- Commands require `BLUEARF_NOVA_API_TOKEN` or `BLUEARF_NOVA_API_KEY`.
- Never print, log, commit, or invent tokens.
- If no token is set, ask the user to provide one or set it in their shell.
- Use `BLUEARF_NOVA_API_URL` only when the user explicitly needs a non-default API base URL.

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
plugins/bluearf-nova/scripts/bluearf-nova vehicles list --company-id COMPANY_ID --limit 25
plugins/bluearf-nova/scripts/bluearf-nova vehicle-models search --brand Toyota --model Corolla --limit 10
plugins/bluearf-nova/scripts/bluearf-nova carbon-records list --company-id COMPANY_ID --year 2024
plugins/bluearf-nova/scripts/bluearf-nova carbon-uniform list --company-id COMPANY_ID --coid COID
plugins/bluearf-nova/scripts/bluearf-nova calculations passenger-commercial-vehicles --company-id COMPANY_ID --coid COID --year 2024
plugins/bluearf-nova/scripts/bluearf-nova calculations passenger-commercial-vehicles --company-id COMPANY_ID --coid COID --year 2024 --input rows.json
```

## SDK Usage

```python
from bluearf_nova import BluearfNova

client = BluearfNova(api_key="BLUEARF_API_TOKEN")
credits = client.credits.get()
vehicles = client.vehicles.list(company_id="COMPANY_ID", limit=25)
```

## Guardrails

- Keep responses concise and summarize large JSON payloads.
- Respect API errors and quota messages; do not retry blindly on insufficient credits.
- For data queries, preserve `company_id`, `organization_id`, `source`, `year`, and `coid` filters exactly as requested.
- Do not use this plugin for internal Firestore writes, Nova backend deploys, or private Firebase session auth.


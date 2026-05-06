# Bluearf Nova API, CLI, and Codex Plugin Guide

This is the customer-facing English guide for the Bluearf Nova Public API,
Python SDK, `bluearf` CLI, and Codex plugin.

## 1. Install

Python SDK:

```bash
pip install bluearf-nova
```

Run from this repository:

```bash
cd python
python3 -m pip install -e .
```

Set your API key:

```bash
export BLUEARF_NOVA_API_KEY="..."
export BLUEARF_NOVA_LANGUAGE="en"
```

The default API URL is `https://api.bluearf.com/v1`. Use
`BLUEARF_NOVA_API_URL` only when you explicitly need a different environment.

`BLUEARF_NOVA_API_TOKEN` is accepted for compatibility. New integrations should
use `BLUEARF_NOVA_API_KEY`.

## 2. Quick Check

```bash
bluearf credits get
bluearf usage list --days 7 --limit 25
bluearf companies list
```

Use Turkish responses when needed:

```bash
bluearf --language tr credits get
```

## 3. Query Accessible Data

Companies:

```bash
bluearf companies list
```

Vehicles:

```bash
bluearf vehicles list --company-id COMPANY_ID --source binek_ticari_araclar --limit 25
```

Vehicle model references:

```bash
bluearf vehicle-models search --brand Toyota --model Corolla --limit 10
```

Carbon records:

```bash
bluearf carbon-records list --company-id COMPANY_ID --year 2024 --source "Binek ve Ticari Araçlar"
```

CarbonDataUniform records:

```bash
bluearf carbon-uniform list --company-id COMPANY_ID --coid COID --year 2024
```

The API does not return raw Firestore documents. Responses are sanitized and
limited by `readAccessIds` and API-key scopes.

## 4. Passenger and Commercial Vehicle Calculation Without Saving

`calculations passenger-commercial-vehicles` is a dry run. It returns an
emission preview and does not create records.

```bash
bluearf calculations passenger-commercial-vehicles \
  --company-id COMPANY_ID \
  --coid COID \
  --year 2024 \
  --input examples/passenger_commercial_rows.en.json
```

Example JSON:

```json
{
  "rows": [
    {
      "vehicleName": "Service-01",
      "ownershipType": "Company Vehicle",
      "vehicleType": "Automobile",
      "fuelTypeName": "Diesel",
      "fuelConsumption": 120,
      "fuelUnit": "Liter",
      "invoiceDate": "2024-03-15"
    }
  ]
}
```

The response includes a `carbonDataPreview`-style result. It does not write
`carbonData`, `vehicleData`, or `CarbonDataUniform`.

## 5. Nova Runs File Pipeline

Nova Runs is the backend-first file pipeline for upload, column matching, value
matching, smart questions, and safe save.

1. Create an upload URL:

```bash
bluearf uploads create \
  --company-id COMPANY_ID \
  --source binek_ticari_araclar \
  --year 2024 \
  --filename fleet.xlsx \
  --content-type application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

2. Upload the file to the returned signed upload URL:

```bash
curl -X PUT \
  -H "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  --upload-file fleet.xlsx \
  "SIGNED_UPLOAD_URL"
```

3. Start the run:

```bash
bluearf nova-runs create \
  --company-id COMPANY_ID \
  --source binek_ticari_araclar \
  --coid FACILITY_ID \
  --year 2024 \
  --file-id FILE_ID \
  --auto-column-match \
  --auto-enrich \
  --auto-safe-save
```

Automation options:

- `--auto-column-match`: automatically advances column matching when backend confidence is safe.
- `--auto-enrich`: uses Nova Assist to fill high-confidence missing values and leaves lower-confidence items for review.
- `--auto-safe-save`: saves automatically only when no blockers remain. This implies `--auto-enrich`.

Track the run:

```bash
bluearf nova-runs get --run-id RUN_ID
bluearf nova-runs export --run-id RUN_ID --limit 100
```

## 6. Smart Questions

When a run cannot continue safely, Nova may generate compact smart questions.
List them:

```bash
bluearf nova-runs questions --run-id RUN_ID --status pending
```

Answer a question:

```bash
bluearf nova-runs answer-question \
  --run-id RUN_ID \
  --question-id QUESTION_ID \
  --answer "Company Vehicle"
```

Skip one question:

```bash
bluearf nova-runs skip-question --run-id RUN_ID --question-id QUESTION_ID
```

Skip all remaining questions:

```bash
bluearf nova-runs skip-question --run-id RUN_ID --remaining
```

Answered questions are applied to the run data. Skipped questions do not write
data.

## 7. Python SDK

```python
import os
from bluearf_nova import BluearfNova

client = BluearfNova(api_key=os.environ["BLUEARF_NOVA_API_KEY"], language="en")

credits = client.credits.get()
companies = client.companies.list()
vehicles = client.vehicles.list(company_id="COMPANY_ID", limit=25)

preview = client.calculations.passenger_commercial_vehicles(
    company_id="COMPANY_ID",
    coid="COID",
    year=2024,
    rows=[
        {
            "vehicleName": "Service-01",
            "ownershipType": "Company Vehicle",
            "vehicleType": "Automobile",
            "fuelTypeName": "Diesel",
            "fuelConsumption": 120,
            "fuelUnit": "Liter",
            "invoiceDate": "2024-03-15",
        }
    ],
)
```

## 8. Codex Plugin

Plugin folder:

```text
plugins/bluearf-nova
```

Before using the plugin in Codex, set the API key:

```bash
export BLUEARF_NOVA_API_KEY="..."
```

Check:

```bash
plugins/bluearf-nova/scripts/check-bluearf-nova
plugins/bluearf-nova/scripts/bluearf-nova credits get
```

The Codex plugin does not store API keys. It reads them from the environment.

## 9. Credit Model

Credits are calculated by endpoint and workload. List endpoints charge by page
size and returned rows. Calculation endpoints charge by input/output row units.
Backend errors are refunded.

Check credits and usage:

```bash
bluearf credits get
bluearf usage list --days 30 --limit 100
```

## 10. Error Format

Errors use a standard JSON shape:

```json
{
  "error": {
    "type": "authentication_error",
    "code": "authentication_failed",
    "message": "Invalid or missing Bluearf API token"
  },
  "request_id": "..."
}
```

Never log or share API keys when debugging auth errors.

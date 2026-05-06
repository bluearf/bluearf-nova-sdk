# bluearf-nova

Python SDK and CLI for the Bluearf Nova Public API.

Default API URL: `https://api.bluearf.com/v1`. Override with
`BLUEARF_NOVA_API_URL` only for non-default environments.

## Install

```bash
pip install bluearf-nova
```

## SDK

```python
import os
from bluearf_nova import BluearfNova

client = BluearfNova(api_key=os.environ["BLUEARF_NOVA_API_KEY"], language="en")

print(client.credits.get())
companies = client.companies.list()
vehicles = client.vehicles.list(company_id="COMPANY_ID", limit=25)

upload = client.uploads.create(
    company_id="COMPANY_ID",
    source="binek_ticari_araclar",
    year=2024,
    filename="fleet.xlsx",
    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
run = client.nova_runs.create(
    company_id="COMPANY_ID",
    source="binek_ticari_araclar",
    coid="FACILITY_ID",
    year=2024,
    file_id=upload["data"]["file_id"],
)

result = client.calculations.passenger_commercial_vehicles(
    company_id="COMPANY_ID",
    coid="VEHICLE_OR_FACILITY_ID",
    year=2024,
    rows=[{"vehicleName": "Vehicle 1", "fuelTypeName": "Gasoline", "fuelConsumption": 100, "fuelUnit": "Liter"}],
)
```

`language` accepts `tr` or `en`. If it is not supplied, the SDK uses `BLUEARF_NOVA_LANGUAGE` and finally defaults to Turkish (`tr`).
Passenger/commercial vehicle calculations accept common English value labels such as `Gasoline`, `Diesel`, `Liter`, `Kilometer`, and `Company Vehicle`; the public API normalizes them to Nova's stored reference values before calculation.

Management calls use a Nova management JWT. The SDK does not perform token
exchange and does not contain third-party Web API keys.

```python
from bluearf_nova import BluearfNovaManagement

management = BluearfNovaManagement(management_token="NOVA_MANAGEMENT_JWT", language="en")
key = management.create_api_key(
    main_company_id="COMPANY_ID",
    display_name="My Nova token",
    expires_in_days=30,
)
print(key["key"]["apiToken"])
```

## CLI

```bash
export BLUEARF_NOVA_API_KEY="BLUEARF_API_KEY"
export BLUEARF_NOVA_LANGUAGE="tr"

bluearf credits get
bluearf companies list
bluearf --language en usage list
bluearf api-keys create --main-company-id COMPANY_ID --display-name "My Nova token" --expires-in-days 30
bluearf uploads create --company-id COMPANY_ID --source binek_ticari_araclar --year 2024 --filename fleet.xlsx
bluearf nova-runs create --company-id COMPANY_ID --source binek_ticari_araclar --coid FACILITY_ID --year 2024 --file-id FILE_ID
bluearf nova-runs create --company-id COMPANY_ID --source binek_ticari_araclar --coid FACILITY_ID --year 2024 --file-id FILE_ID --auto-column-match --auto-enrich --auto-safe-save
bluearf nova-runs get --run-id RUN_ID
bluearf nova-runs questions --run-id RUN_ID --status pending
bluearf nova-runs answer-question --run-id RUN_ID --question-id QUESTION_ID --answer "Company vehicle"
bluearf nova-runs skip-question --run-id RUN_ID --question-id QUESTION_ID
bluearf nova-runs skip-question --run-id RUN_ID --remaining
bluearf nova-runs export --run-id RUN_ID --limit 100
bluearf vehicles list --company-id COMPANY_ID
bluearf vehicle-models search --brand Toyota --model Corolla
bluearf carbon-records list --company-id COMPANY_ID
bluearf carbon-uniform list --company-id COMPANY_ID --coid COID
bluearf calculations passenger-commercial-vehicles --company-id COMPANY_ID --coid COID --year 2024 --input rows.json
```

Passenger/commercial vehicle calculations are dry-run by design: they return a `carbonDataPreview` and do not create `carbonData`, `vehicleData`, or `CarbonDataUniform` records.

Nova Runs automation flags:

- `--auto-column-match`: safely advances column matching when backend confidence is sufficient.
- `--auto-enrich`: uses Nova Assist to fill high-confidence missing values and leave lower-confidence values for review.
- `--auto-safe-save`: saves only if no blockers remain; this implies `--auto-enrich`.

`api-keys create` uses the Nova management backend and requires a Nova
management JWT:

```bash
export BLUEARF_NOVA_MANAGEMENT_TOKEN="..."
bluearf api-keys create --main-company-id COMPANY_ID --display-name "My Nova token" --expires-in-days 30
```

## Credit model

Credits are calculated by endpoint and workload. List endpoints reserve by
requested page size and settle by returned rows. Calculation endpoints reserve
and settle by input/output row units. Backend errors are refunded automatically.

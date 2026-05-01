# bluearf-nova

Python SDK and CLI for the Bluearf Nova Public API.

## Install

```bash
pip install bluearf-nova
```

## SDK

```python
from bluearf_nova import BluearfNova

client = BluearfNova(api_key="BLUEARF_API_TOKEN")

print(client.credits.get())
vehicles = client.vehicles.list(company_id="COMPANY_ID", limit=25)
result = client.calculations.passenger_commercial_vehicles(
    company_id="COMPANY_ID",
    coid="VEHICLE_OR_FACILITY_ID",
    year=2024,
)
```

## CLI

```bash
export BLUEARF_NOVA_API_TOKEN="BLUEARF_API_TOKEN"

bluearf credits get
bluearf usage list
bluearf vehicles list --company-id COMPANY_ID
bluearf vehicle-models search --brand Toyota --model Corolla
bluearf carbon-records list --company-id COMPANY_ID
bluearf carbon-uniform list --company-id COMPANY_ID --coid COID
bluearf calculations passenger-commercial-vehicles --company-id COMPANY_ID --coid COID --year 2024
```

## Credit model

Credits are calculated by endpoint and workload. List endpoints reserve by
requested page size and settle by returned rows. Calculation endpoints reserve
and settle by input/output row units. Backend errors are refunded automatically.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from .client import BluearfAPIError, BluearfNova


def _print(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def _client(args: argparse.Namespace) -> BluearfNova:
    return BluearfNova(api_key=args.api_key, base_url=args.base_url)


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--api-key", default=None, help="Bluearf API token. Defaults to BLUEARF_NOVA_API_TOKEN.")
    parser.add_argument("--base-url", default=None, help="Bluearf Nova API base URL.")


def _add_list_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--cursor", default=None)
    parser.add_argument("--source", default=None)
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--coid", default=None)


def _load_json_payload(path: str | None) -> Dict[str, Any]:
    if not path:
        return {}
    raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    parsed = json.loads(raw or "{}")
    if isinstance(parsed, list):
        return {"rows": parsed}
    if isinstance(parsed, dict):
        return parsed
    raise SystemExit("--input must contain a JSON object or array")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bluearf", description="Bluearf Nova API CLI")
    _add_common(parser)
    sub = parser.add_subparsers(dest="resource", required=True)

    credits = sub.add_parser("credits")
    credits_sub = credits.add_subparsers(dest="action", required=True)
    credits_sub.add_parser("get")

    usage = sub.add_parser("usage")
    usage_sub = usage.add_subparsers(dest="action", required=True)
    usage_list = usage_sub.add_parser("list")
    usage_list.add_argument("--days", type=int, default=None)
    usage_list.add_argument("--limit", type=int, default=None)

    vehicles = sub.add_parser("vehicles")
    vehicles_sub = vehicles.add_subparsers(dest="action", required=True)
    vehicles_list = vehicles_sub.add_parser("list")
    vehicles_list.add_argument("--company-id", required=True)
    _add_list_filters(vehicles_list)

    models = sub.add_parser("vehicle-models")
    models_sub = models.add_subparsers(dest="action", required=True)
    models_search = models_sub.add_parser("search")
    models_search.add_argument("--brand", default=None)
    models_search.add_argument("--model", default=None)
    models_search.add_argument("--fuel-type", default=None)
    models_search.add_argument("--year", type=int, default=None)
    models_search.add_argument("--engine", default=None)
    models_search.add_argument("--limit", type=int, default=None)

    carbon_records = sub.add_parser("carbon-records")
    carbon_records_sub = carbon_records.add_subparsers(dest="action", required=True)
    carbon_records_list = carbon_records_sub.add_parser("list")
    carbon_records_list.add_argument("--company-id", required=True)
    _add_list_filters(carbon_records_list)

    carbon_uniform = sub.add_parser("carbon-uniform")
    carbon_uniform_sub = carbon_uniform.add_subparsers(dest="action", required=True)
    carbon_uniform_list = carbon_uniform_sub.add_parser("list")
    carbon_uniform_list.add_argument("--company-id", default=None)
    carbon_uniform_list.add_argument("--organization-id", default=None)
    _add_list_filters(carbon_uniform_list)

    calculations = sub.add_parser("calculations")
    calculations_sub = calculations.add_subparsers(dest="action", required=True)
    calc = calculations_sub.add_parser("passenger-commercial-vehicles")
    calc.add_argument("--company-id", required=True)
    calc.add_argument("--coid", required=True)
    calc.add_argument("--year", required=True, type=int)
    calc.add_argument("--input", default=None, help="Optional JSON object/array payload. Use '-' for stdin.")

    return parser


def run(args: argparse.Namespace) -> Dict[str, Any]:
    client = _client(args)
    if args.resource == "credits":
        return client.credits.get()
    if args.resource == "usage":
        return client.usage.list(days=getattr(args, "days", None), limit=getattr(args, "limit", None))
    if args.resource == "vehicles":
        return client.vehicles.list(
            company_id=args.company_id,
            limit=args.limit,
            cursor=args.cursor,
            source=args.source,
            year=args.year,
            coid=args.coid,
        )
    if args.resource == "vehicle-models":
        return client.vehicle_models.search(
            brand=args.brand,
            model=args.model,
            fuelType=args.fuel_type,
            year=args.year,
            engine=args.engine,
            limit=args.limit,
        )
    if args.resource == "carbon-records":
        return client.carbon_records.list(
            company_id=args.company_id,
            limit=args.limit,
            cursor=args.cursor,
            source=args.source,
            year=args.year,
            coid=args.coid,
        )
    if args.resource == "carbon-uniform":
        return client.carbon_uniform.list(
            company_id=args.company_id,
            organization_id=args.organization_id,
            limit=args.limit,
            cursor=args.cursor,
            source=args.source,
            year=args.year,
            coid=args.coid,
        )
    if args.resource == "calculations":
        payload = _load_json_payload(getattr(args, "input", None))
        return client.calculations.passenger_commercial_vehicles(
            company_id=args.company_id,
            coid=args.coid,
            year=args.year,
            **payload,
        )
    raise SystemExit(f"Unknown command: {args.resource}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        _print(run(args))
        return 0
    except BluearfAPIError as exc:
        _print(exc.response)
        return 1


if __name__ == "__main__":
    sys.exit(main())

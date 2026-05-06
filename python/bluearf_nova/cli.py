from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from .client import BluearfAPIError, BluearfNova, BluearfNovaManagement


def _print(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def _client(args: argparse.Namespace) -> BluearfNova:
    return BluearfNova(api_key=args.api_key, base_url=args.base_url, language=args.language)


def _management_client(args: argparse.Namespace) -> BluearfNovaManagement:
    return BluearfNovaManagement(
        management_token=args.management_token,
        base_url=args.management_url,
        language=args.language,
    )


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--api-key", default=None, help="Bluearf API key. Defaults to BLUEARF_NOVA_API_KEY.")
    parser.add_argument("--base-url", default=None, help="Bluearf Nova API base URL.")
    parser.add_argument(
        "--language",
        choices=["tr", "en"],
        default=None,
        help="Response language. Defaults to BLUEARF_NOVA_LANGUAGE or tr.",
    )
    parser.add_argument("--management-token", default=None, help="Nova management JWT. Defaults to BLUEARF_NOVA_MANAGEMENT_TOKEN.")
    parser.add_argument("--management-url", default=None, help="Bluearf Nova management API base URL.")


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


def _load_json_object(path: str | None, *, label: str) -> Dict[str, Any]:
    if not path:
        return {}
    raw = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    parsed = json.loads(raw or "{}")
    if isinstance(parsed, dict):
        return parsed
    raise SystemExit(f"{label} must contain a JSON object")


def _automation_profile_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    profile = _load_json_object(getattr(args, "automation_profile", None), label="--automation-profile")
    if not profile:
        profile = {}
    profile["autoColumnMatch"] = bool(profile.get("autoColumnMatch") or getattr(args, "auto_column_match", False))
    profile["autoEnrich"] = bool(profile.get("autoEnrich") or getattr(args, "auto_enrich", False))
    profile["autoSafeSave"] = bool(profile.get("autoSafeSave") or getattr(args, "auto_safe_save", False))
    if profile["autoSafeSave"]:
        profile["autoEnrich"] = True
    return profile


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

    companies = sub.add_parser("companies")
    companies_sub = companies.add_subparsers(dest="action", required=True)
    companies_list = companies_sub.add_parser("list")
    companies_list.add_argument("--company-id", default=None)
    companies_list.add_argument("--fields", default=None)

    api_keys = sub.add_parser("api-keys")
    api_keys_sub = api_keys.add_subparsers(dest="action", required=True)
    api_key_create = api_keys_sub.add_parser("create")
    api_key_create.add_argument("--main-company-id", required=True)
    api_key_create.add_argument("--company-id", action="append", dest="company_ids", default=None)
    api_key_create.add_argument("--display-name", default="Nova API key")
    api_key_create.add_argument("--expires-in-days", type=int, default=30)
    api_key_create.add_argument("--service", action="append", dest="services", default=None)
    api_key_create.add_argument("--restrictions", default=None, help="Optional JSON object path for restrictions.")

    uploads = sub.add_parser("uploads")
    uploads_sub = uploads.add_subparsers(dest="action", required=True)
    upload_create = uploads_sub.add_parser("create")
    upload_create.add_argument("--company-id", required=True)
    upload_create.add_argument("--source", required=True)
    upload_create.add_argument("--year", required=True, type=int)
    upload_create.add_argument("--filename", required=True)
    upload_create.add_argument("--content-type", default=None)
    upload_create.add_argument("--size-bytes", type=int, default=None)
    upload_create.add_argument("--task-id", default=None)
    upload_create.add_argument("--expires-minutes", type=int, default=None)

    nova_runs = sub.add_parser("nova-runs")
    nova_runs_sub = nova_runs.add_subparsers(dest="action", required=True)
    nova_run_create = nova_runs_sub.add_parser("create")
    nova_run_create.add_argument("--company-id", required=True)
    nova_run_create.add_argument("--source", required=True)
    nova_run_create.add_argument("--coid", required=True)
    nova_run_create.add_argument("--year", required=True, type=int)
    nova_run_create.add_argument("--file-id", required=True)
    nova_run_create.add_argument("--storage-path", default=None)
    nova_run_create.add_argument("--filename", default=None)
    nova_run_create.add_argument("--sheet-name", default=None)
    nova_run_create.add_argument("--checksum", default=None)
    nova_run_create.add_argument("--run-id", default=None)
    nova_run_create.add_argument("--auto-column-match", action="store_true", help="Safely advance column matching when backend confidence is sufficient.")
    nova_run_create.add_argument("--auto-enrich", action="store_true", help="Use Nova Assist to fill high-confidence missing values and leave lower-confidence items for review.")
    nova_run_create.add_argument("--auto-safe-save", action="store_true", help="Save automatically only when Nova Assist is enabled and no blocker remains.")
    nova_run_create.add_argument("--automation-profile", default=None, help="Optional JSON object path for advanced automationProfile settings.")
    nova_run_get = nova_runs_sub.add_parser("get")
    nova_run_get.add_argument("--run-id", required=True)
    nova_run_export = nova_runs_sub.add_parser("export")
    nova_run_export.add_argument("--run-id", required=True)
    nova_run_export.add_argument("--limit", type=int, default=None)
    nova_run_export.add_argument("--content-id", default=None)
    nova_run_questions = nova_runs_sub.add_parser("questions")
    nova_run_questions.add_argument("--run-id", required=True)
    nova_run_questions.add_argument("--status", default=None)
    nova_run_questions.add_argument("--limit", type=int, default=None)
    nova_run_questions.add_argument("--cursor", default=None)
    nova_run_questions.add_argument("--content-id", default=None)
    nova_run_answer = nova_runs_sub.add_parser("answer-question")
    nova_run_answer.add_argument("--run-id", required=True)
    nova_run_answer.add_argument("--question-id", required=True)
    nova_run_answer.add_argument("--answer", required=True)
    nova_run_answer.add_argument("--content-id", default=None)
    nova_run_skip = nova_runs_sub.add_parser("skip-question")
    nova_run_skip.add_argument("--run-id", required=True)
    nova_run_skip.add_argument("--question-id", default=None)
    nova_run_skip.add_argument("--remaining", action="store_true", help="Skip this question and all remaining pending smart questions.")
    nova_run_skip.add_argument("--content-id", default=None)

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
    calc = calculations_sub.add_parser(
        "passenger-commercial-vehicles",
        aliases=["passenger-commercial-vehicles-preview"],
        help="Calculate passenger/commercial vehicle emissions without saving records.",
    )
    calc.add_argument("--company-id", required=True)
    calc.add_argument("--coid", required=True)
    calc.add_argument("--year", required=True, type=int)
    calc.add_argument("--input", default=None, help="Optional JSON object/array payload. Use '-' for stdin.")

    return parser


def run(args: argparse.Namespace) -> Dict[str, Any]:
    if args.resource == "api-keys":
        client = _management_client(args)
        if args.action == "create":
            restrictions = _load_json_payload(args.restrictions) if args.restrictions else None
            return client.create_api_key(
                main_company_id=args.main_company_id,
                company_ids=args.company_ids,
                display_name=args.display_name,
                expires_in_days=args.expires_in_days,
                services=args.services,
                restrictions=restrictions,
            )
    client = _client(args)
    if args.resource == "credits":
        return client.credits.get()
    if args.resource == "usage":
        return client.usage.list(days=getattr(args, "days", None), limit=getattr(args, "limit", None))
    if args.resource == "companies":
        return client.companies.list(company_id=args.company_id, fields=args.fields)
    if args.resource == "uploads":
        return client.uploads.create(
            company_id=args.company_id,
            source=args.source,
            year=args.year,
            filename=args.filename,
            content_type=args.content_type,
            size_bytes=args.size_bytes,
            task_id=args.task_id,
            expires_minutes=args.expires_minutes,
        )
    if args.resource == "nova-runs":
        if args.action == "create":
            automation_profile = _automation_profile_from_args(args)
            return client.nova_runs.create(
                company_id=args.company_id,
                source=args.source,
                coid=args.coid,
                year=args.year,
                file_id=args.file_id,
                storage_path=args.storage_path,
                filename=args.filename,
                sheet_name=args.sheet_name,
                checksum=args.checksum,
                run_id=args.run_id,
                automationProfile=automation_profile,
            )
        if args.action == "get":
            return client.nova_runs.get(run_id=args.run_id)
        if args.action == "export":
            return client.nova_runs.export(
                run_id=args.run_id,
                limit=args.limit,
                content_id=args.content_id,
            )
        if args.action == "questions":
            return client.nova_runs.questions(
                run_id=args.run_id,
                status=args.status,
                limit=args.limit,
                cursor=args.cursor,
                content_id=args.content_id,
            )
        if args.action == "answer-question":
            return client.nova_runs.answer_question(
                run_id=args.run_id,
                question_id=args.question_id,
                answer=args.answer,
                content_id=args.content_id,
            )
        if args.action == "skip-question":
            return client.nova_runs.skip_question(
                run_id=args.run_id,
                question_id=args.question_id,
                skip_remaining=args.remaining,
                content_id=args.content_id,
            )
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
    except ValueError as exc:
        _print({"error": {"message": str(exc)}})
        return 1


if __name__ == "__main__":
    sys.exit(main())

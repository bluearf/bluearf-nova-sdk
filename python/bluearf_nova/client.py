from __future__ import annotations

import os
import json as json_module
from typing import Any, Dict, Optional
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://api.bluearf.com/v1"
DEFAULT_MANAGEMENT_BASE_URL = "https://api.bluearf.com"


class BluearfAPIError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response: Dict[str, Any],
        response_headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        self.response_headers = response_headers or {}


class _Resource:
    def __init__(self, client: "BluearfNova"):
        self._client = client


def _normalize_language(language: Optional[str]) -> str:
    value = str(language or "").strip().lower()
    return "en" if value.startswith("en") else "tr"


class CreditsResource(_Resource):
    def get(self) -> Dict[str, Any]:
        return self._client.get("/credits")


class UsageResource(_Resource):
    def list(self, **params: Any) -> Dict[str, Any]:
        return self._client.get("/usage", params=params)


class CompaniesResource(_Resource):
    def list(self, **params: Any) -> Dict[str, Any]:
        return self._client.get("/companies", params=params)


class UploadsResource(_Resource):
    def create(
        self,
        *,
        company_id: str,
        source: str,
        year: int,
        filename: str,
        **payload: Any,
    ) -> Dict[str, Any]:
        return self._client.post(
            "/uploads",
            json={
                "company_id": company_id,
                "source": source,
                "year": year,
                "filename": filename,
                **payload,
            },
        )


class NovaRunsResource(_Resource):
    def create(
        self,
        *,
        company_id: str,
        source: str,
        coid: str,
        year: int,
        file_id: str,
        **payload: Any,
    ) -> Dict[str, Any]:
        return self._client.post(
            "/nova-runs",
            json={
                "company_id": company_id,
                "source": source,
                "coid": coid,
                "year": year,
                "file_id": file_id,
                **payload,
            },
        )

    def get(self, *, run_id: str, **params: Any) -> Dict[str, Any]:
        return self._client.get("/nova-runs", params={"run_id": run_id, **params})

    def export(self, *, run_id: str, **params: Any) -> Dict[str, Any]:
        return self._client.get("/nova-runs/export", params={"run_id": run_id, **params})

    def questions(self, *, run_id: str, **params: Any) -> Dict[str, Any]:
        return self._client.get("/nova-runs/questions", params={"run_id": run_id, **params})

    def answer_question(self, *, run_id: str, question_id: str, answer: Any, **payload: Any) -> Dict[str, Any]:
        return self._client.post(
            "/nova-runs/questions/answer",
            json={"run_id": run_id, "question_id": question_id, "answer": answer, **payload},
        )

    def skip_question(self, *, run_id: str, question_id: Optional[str] = None, skip_remaining: bool = False, **payload: Any) -> Dict[str, Any]:
        body = {"run_id": run_id, "skip_remaining": skip_remaining, **payload}
        if question_id:
            body["question_id"] = question_id
        return self._client.post("/nova-runs/questions/skip", json=body)


class VehiclesResource(_Resource):
    def list(self, *, company_id: str, **params: Any) -> Dict[str, Any]:
        return self._client.get("/vehicles", params={"company_id": company_id, **params})


class VehicleModelsResource(_Resource):
    def search(self, **params: Any) -> Dict[str, Any]:
        return self._client.get("/vehicle-models", params=params)


class CarbonRecordsResource(_Resource):
    def list(self, *, company_id: str, **params: Any) -> Dict[str, Any]:
        return self._client.get("/carbon-records", params={"company_id": company_id, **params})


class CarbonUniformResource(_Resource):
    def list(self, **params: Any) -> Dict[str, Any]:
        return self._client.get("/carbon-uniform", params=params)


class CalculationsResource(_Resource):
    def passenger_commercial_vehicles(
        self,
        *,
        company_id: str,
        coid: str,
        year: int,
        **payload: Any,
    ) -> Dict[str, Any]:
        return self._client.post(
            "/calculations/passenger-commercial-vehicles",
            json={"company_id": company_id, "coid": coid, "year": year, **payload},
        )

    def passenger_commercial_vehicles_preview(
        self,
        *,
        company_id: str,
        coid: str,
        year: int,
        **payload: Any,
    ) -> Dict[str, Any]:
        """Calculate passenger/commercial vehicle emissions without saving records."""
        return self.passenger_commercial_vehicles(
            company_id=company_id,
            coid=coid,
            year=year,
            **payload,
        )


class BluearfNova:
    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        language: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key or os.getenv("BLUEARF_NOVA_API_KEY") or os.getenv("BLUEARF_NOVA_API_TOKEN")
        if not self.api_key:
            raise ValueError("Bluearf API key is required. Pass api_key or set BLUEARF_NOVA_API_KEY.")
        self.base_url = (base_url or os.getenv("BLUEARF_NOVA_API_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.language = _normalize_language(
            language
            or os.getenv("BLUEARF_NOVA_LANGUAGE")
        )
        self.timeout = timeout
        self.last_response_headers: Dict[str, str] = {}

        self.credits = CreditsResource(self)
        self.usage = UsageResource(self)
        self.companies = CompaniesResource(self)
        self.uploads = UploadsResource(self)
        self.nova_runs = NovaRunsResource(self)
        self.vehicles = VehiclesResource(self)
        self.vehicle_models = VehicleModelsResource(self)
        self.carbon_records = CarbonRecordsResource(self)
        self.carbon_uniform = CarbonUniformResource(self)
        self.calculations = CalculationsResource(self)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}
        clean_params.setdefault("language", self.language)
        query = f"?{urlencode(clean_params, doseq=True)}" if clean_params else ""
        request_headers = dict(headers or {})
        request_headers.setdefault("Authorization", f"Bearer {self.api_key}")
        request_headers.setdefault("Accept", "application/json")
        data = None
        if json is not None:
            body = dict(json)
            body.setdefault("language", self.language)
            data = json_module.dumps(body).encode("utf-8")
            request_headers.setdefault("Content-Type", "application/json")
        request = Request(
            f"{self.base_url}{path}{query}",
            data=data,
            headers=request_headers,
            method=method.upper(),
        )
        status_code = 0
        raw_body = ""
        response_headers: Dict[str, str] = {}
        try:
            with urlopen(request, timeout=self.timeout) as response:
                status_code = int(getattr(response, "status", 200) or 200)
                response_headers = dict(response.headers.items())
                raw_body = response.read().decode("utf-8")
        except HTTPError as exc:
            status_code = int(exc.code or 0)
            response_headers = dict(exc.headers.items()) if exc.headers else {}
            raw_body = exc.read().decode("utf-8", errors="replace")
        self.last_response_headers = response_headers
        try:
            payload = json_module.loads(raw_body or "{}")
        except ValueError:
            payload = {"error": {"message": raw_body}}
        if status_code >= 400:
            error = payload.get("error") if isinstance(payload, dict) else {}
            message = error.get("message") if isinstance(error, dict) else None
            raise BluearfAPIError(
                message or f"Bluearf API request failed with status {status_code}",
                status_code=status_code,
                response=payload if isinstance(payload, dict) else {"data": payload},
                response_headers=response_headers,
            )
        return payload if isinstance(payload, dict) else {"data": payload}

    @property
    def credits_remaining(self) -> Optional[str]:
        return self.last_response_headers.get("X-Bluearf-Credits-Remaining")

    def get(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.request("POST", path, json=json or {})


class BluearfNovaManagement:
    def __init__(
        self,
        management_token: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        language: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.management_token = (
            management_token
            or os.getenv("BLUEARF_NOVA_MANAGEMENT_TOKEN")
        )
        if not self.management_token:
            raise ValueError(
                "Nova management JWT is required. Set BLUEARF_NOVA_MANAGEMENT_TOKEN or pass --management-token."
            )
        self.base_url = (
            base_url
            or os.getenv("BLUEARF_NOVA_MANAGEMENT_URL")
            or os.getenv("BLUEARF_NOVA_API_MANAGEMENT_URL")
            or DEFAULT_MANAGEMENT_BASE_URL
        ).rstrip("/")
        self.language = _normalize_language(
            language
            or os.getenv("BLUEARF_NOVA_LANGUAGE")
        )
        self.timeout = timeout

    def request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = dict(payload or {})
        body.setdefault("language", self.language)
        request = Request(
            self.base_url,
            data=json_module.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.management_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        status_code = 0
        raw_body = ""
        response_headers: Dict[str, str] = {}
        try:
            with urlopen(request, timeout=self.timeout) as response:
                status_code = int(getattr(response, "status", 200) or 200)
                response_headers = dict(response.headers.items())
                raw_body = response.read().decode("utf-8")
        except HTTPError as exc:
            status_code = int(exc.code or 0)
            response_headers = dict(exc.headers.items()) if exc.headers else {}
            raw_body = exc.read().decode("utf-8", errors="replace")
        try:
            body = json_module.loads(raw_body or "{}")
        except ValueError:
            body = {"error": {"message": raw_body}}
        if status_code >= 400:
            error = body.get("error") if isinstance(body, dict) else {}
            message = error.get("message") if isinstance(error, dict) else None
            raise BluearfAPIError(
                message or f"Bluearf management request failed with status {status_code}",
                status_code=status_code,
                response=body if isinstance(body, dict) else {"data": body},
                response_headers=response_headers,
            )
        return body if isinstance(body, dict) else {"data": body}

    def create_api_key(
        self,
        *,
        main_company_id: str,
        company_ids: Optional[list[str]] = None,
        display_name: Optional[str] = None,
        expires_in_days: int = 30,
        services: Optional[list[str]] = None,
        restrictions: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.request(
            {
                "req_type": "nova_api_keys_create",
                "main_company_id": main_company_id,
                "company_ids": company_ids or [main_company_id],
                "display_name": display_name or "Nova API key",
                "expires_in_days": expires_in_days,
                **({"services": services} if services else {}),
                **({"restrictions": restrictions} if restrictions else {}),
            }
        )

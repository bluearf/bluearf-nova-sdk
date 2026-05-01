from __future__ import annotations

import os
import json as json_module
from typing import Any, Dict, Optional
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://bluearf-nova-api-walbuhs3uq-uc.a.run.app/v1"


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


class CreditsResource(_Resource):
    def get(self) -> Dict[str, Any]:
        return self._client.get("/credits")


class UsageResource(_Resource):
    def list(self, **params: Any) -> Dict[str, Any]:
        return self._client.get("/usage", params=params)


class CompaniesResource(_Resource):
    def list(self, **params: Any) -> Dict[str, Any]:
        return self._client.get("/companies", params=params)


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


class BluearfNova:
    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key or os.getenv("BLUEARF_NOVA_API_TOKEN") or os.getenv("BLUEARF_NOVA_API_KEY")
        if not self.api_key:
            raise ValueError("Bluearf API token is required. Pass api_key or set BLUEARF_NOVA_API_TOKEN.")
        self.base_url = (base_url or os.getenv("BLUEARF_NOVA_API_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.last_response_headers: Dict[str, str] = {}

        self.credits = CreditsResource(self)
        self.usage = UsageResource(self)
        self.companies = CompaniesResource(self)
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
        query = f"?{urlencode(clean_params, doseq=True)}" if clean_params else ""
        request_headers = dict(headers or {})
        request_headers.setdefault("Authorization", f"Bearer {self.api_key}")
        request_headers.setdefault("Accept", "application/json")
        data = None
        if json is not None:
            data = json_module.dumps(json).encode("utf-8")
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

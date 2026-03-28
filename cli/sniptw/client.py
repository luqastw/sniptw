"""HTTP client for API communication."""

from typing import Any

import httpx
from rich.console import Console

from cli.sniptw.config import get_api_url, get_token

console = Console()


class APIError(Exception):
    """Custom exception for API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class APIClient:
    """HTTP client for sniptw API."""

    def __init__(self, timeout: float = 10.0):
        self.base_url = get_api_url()
        self.timeout = timeout

    def _get_headers(self, authenticated: bool = False) -> dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if authenticated:
            token = get_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise appropriate errors."""
        if response.status_code == 401:
            detail = response.json().get("detail", "Not authenticated")
            raise APIError(detail, 401)
        if response.status_code == 403:
            raise APIError("Permission denied.", 403)
        if response.status_code == 404:
            raise APIError("Resource not found.", 404)
        if response.status_code == 409:
            detail = response.json().get("detail", "Conflict")
            raise APIError(detail, 409)
        if response.status_code == 422:
            detail = response.json().get("detail", "Validation error")
            if isinstance(detail, list):
                errors = [
                    f"{e.get('loc', ['?'])[-1]}: {e.get('msg', '?')}" for e in detail
                ]
                raise APIError("Validation error: " + "; ".join(errors), 422)
            raise APIError(f"Validation error: {detail}", 422)
        if response.status_code >= 400:
            detail = response.json().get("detail", "Unknown error")
            raise APIError(str(detail), response.status_code)

        if response.status_code == 204:
            return {}

        return response.json()

    def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        authenticated: bool = False,
        form_data: bool = False,
    ) -> dict[str, Any]:
        """Make a POST request."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(authenticated)

        with httpx.Client(timeout=self.timeout) as client:
            if form_data:
                headers.pop("Content-Type", None)
                response = client.post(url, data=data, headers=headers)
            else:
                response = client.post(url, json=data, headers=headers)
            return self._handle_response(response)

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        authenticated: bool = False,
    ) -> dict[str, Any]:
        """Make a GET request."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(authenticated)

        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params, headers=headers)
            return self._handle_response(response)

    def patch(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        """Make a PATCH request."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(authenticated)

        with httpx.Client(timeout=self.timeout) as client:
            response = client.patch(url, json=data, headers=headers)
            return self._handle_response(response)

    def delete(
        self,
        endpoint: str,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        """Make a DELETE request."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(authenticated)

        with httpx.Client(timeout=self.timeout) as client:
            response = client.delete(url, headers=headers)
            return self._handle_response(response)


def get_client() -> APIClient:
    """Get an API client instance."""
    return APIClient()

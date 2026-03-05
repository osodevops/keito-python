from __future__ import annotations

import contextlib
import random
import time
from typing import Any, Optional, TypeVar

import httpx

from keito._version import VERSION
from keito.core.api_error import (
    KeitoApiError,
    KeitoAuthError,
    KeitoConflictError,
    KeitoConnectionError,
    KeitoForbiddenError,
    KeitoNotFoundError,
    KeitoRateLimitError,
    KeitoServerError,
    KeitoTimeoutError,
    KeitoValidationError,
)
from keito.core.request_options import RequestOptions

T = TypeVar("T")

_RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
_IDEMPOTENT_METHODS = {"GET", "PUT", "DELETE", "HEAD", "OPTIONS"}

_ERROR_MAP: dict[int, type[KeitoApiError]] = {
    400: KeitoValidationError,
    401: KeitoAuthError,
    403: KeitoForbiddenError,
    404: KeitoNotFoundError,
    409: KeitoConflictError,
}


def _calculate_backoff(attempt: int) -> float:
    base = min(2 ** (attempt - 1) * 0.5, 8.0)
    jitter = random.random() * base * 0.5
    return base + jitter


def _parse_retry_after(response: httpx.Response) -> Optional[float]:
    header = response.headers.get("retry-after")
    if header is None:
        return None
    try:
        return float(header)
    except ValueError:
        return None


def _raise_for_status(response: httpx.Response) -> None:
    if response.is_success:
        return

    body: Optional[dict[str, Any]] = None
    with contextlib.suppress(Exception):
        body = response.json()

    kwargs: dict[str, Any] = {
        "body": body,
        "headers": response.headers,
        "raw_response": response,
    }

    status = response.status_code

    if status == 429:
        retry_after = _parse_retry_after(response)
        raise KeitoRateLimitError(retry_after=retry_after, **kwargs)

    if status in _ERROR_MAP:
        raise _ERROR_MAP[status](**kwargs)

    if 500 <= status < 600:
        raise KeitoServerError(status_code=status, **kwargs)

    raise KeitoApiError(
        f"Unexpected status code: {status}",
        status_code=status,
        **kwargs,
    )


class HttpClient:
    """Synchronous HTTP client with retry logic."""

    def __init__(
        self,
        *,
        api_key: str,
        account_id: str,
        base_url: str = "https://app.keito.io",
        timeout: float = 60.0,
        max_retries: int = 2,
        httpx_client: Optional[httpx.Client] = None,
    ) -> None:
        self._api_key = api_key
        self._account_id = account_id
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._owns_client = httpx_client is None
        self._client = httpx_client or httpx.Client()

    def _build_headers(self, extra: Optional[dict[str, Any]] = None) -> dict[str, str]:
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._api_key}",
            "Keito-Account-Id": self._account_id,
            "User-Agent": f"keito-python/{VERSION}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if extra:
            headers.update({k: str(v) for k, v in extra.items()})
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> httpx.Response:
        opts = request_options or {}
        max_retries = opts.get("max_retries") if opts.get("max_retries") is not None else self._max_retries
        timeout = opts.get("timeout") if opts.get("timeout") is not None else self._timeout
        extra_headers = opts.get("additional_headers")

        url = f"{self._base_url}{path}"
        headers = self._build_headers(extra_headers)

        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        is_idempotent = method.upper() in _IDEMPOTENT_METHODS
        last_exc: Optional[Exception] = None

        for attempt in range(max_retries + 1):
            try:
                response = self._client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    json=json,
                    params=params,
                    timeout=timeout,
                )
            except httpx.TimeoutException as e:
                last_exc = e
                if attempt < max_retries and is_idempotent:
                    time.sleep(_calculate_backoff(attempt + 1))
                    continue
                raise KeitoTimeoutError(str(e)) from e
            except httpx.ConnectError as e:
                last_exc = e
                if attempt < max_retries and is_idempotent:
                    time.sleep(_calculate_backoff(attempt + 1))
                    continue
                raise KeitoConnectionError(str(e)) from e

            if response.status_code in _RETRYABLE_STATUS_CODES and attempt < max_retries:
                if not is_idempotent and method.upper() == "POST":
                    # Only retry POST if it's explicitly allowed (not by default)
                    _raise_for_status(response)

                if response.status_code == 429:
                    retry_after = _parse_retry_after(response)
                    if retry_after is not None:
                        time.sleep(retry_after)
                        continue

                time.sleep(_calculate_backoff(attempt + 1))
                continue

            _raise_for_status(response)
            return response

        # Should not reach here, but handle gracefully
        if last_exc:
            raise last_exc
        raise KeitoApiError("Max retries exceeded", status_code=0)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()


class AsyncHttpClient:
    """Asynchronous HTTP client with retry logic."""

    def __init__(
        self,
        *,
        api_key: str,
        account_id: str,
        base_url: str = "https://app.keito.io",
        timeout: float = 60.0,
        max_retries: int = 2,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._api_key = api_key
        self._account_id = account_id
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._owns_client = httpx_client is None
        self._client = httpx_client or httpx.AsyncClient()

    def _build_headers(self, extra: Optional[dict[str, Any]] = None) -> dict[str, str]:
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._api_key}",
            "Keito-Account-Id": self._account_id,
            "User-Agent": f"keito-python/{VERSION}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if extra:
            headers.update({k: str(v) for k, v in extra.items()})
        return headers

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> httpx.Response:
        import asyncio

        opts = request_options or {}
        max_retries = opts.get("max_retries") if opts.get("max_retries") is not None else self._max_retries
        timeout = opts.get("timeout") if opts.get("timeout") is not None else self._timeout
        extra_headers = opts.get("additional_headers")

        url = f"{self._base_url}{path}"
        headers = self._build_headers(extra_headers)

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        is_idempotent = method.upper() in _IDEMPOTENT_METHODS
        last_exc: Optional[Exception] = None

        for attempt in range(max_retries + 1):
            try:
                response = await self._client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    json=json,
                    params=params,
                    timeout=timeout,
                )
            except httpx.TimeoutException as e:
                last_exc = e
                if attempt < max_retries and is_idempotent:
                    await asyncio.sleep(_calculate_backoff(attempt + 1))
                    continue
                raise KeitoTimeoutError(str(e)) from e
            except httpx.ConnectError as e:
                last_exc = e
                if attempt < max_retries and is_idempotent:
                    await asyncio.sleep(_calculate_backoff(attempt + 1))
                    continue
                raise KeitoConnectionError(str(e)) from e

            if response.status_code in _RETRYABLE_STATUS_CODES and attempt < max_retries:
                if not is_idempotent and method.upper() == "POST":
                    _raise_for_status(response)

                if response.status_code == 429:
                    retry_after = _parse_retry_after(response)
                    if retry_after is not None:
                        await asyncio.sleep(retry_after)
                        continue

                await asyncio.sleep(_calculate_backoff(attempt + 1))
                continue

            _raise_for_status(response)
            return response

        if last_exc:
            raise last_exc
        raise KeitoApiError("Max retries exceeded", status_code=0)

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

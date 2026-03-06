from __future__ import annotations

from typing import Any, Generic, TypeVar

import httpx

T = TypeVar("T")


class RawResponse(Generic[T]):
    """Wraps a parsed response with access to the raw httpx response."""

    def __init__(self, *, data: T, response: httpx.Response) -> None:
        self.data = data
        self.status_code = response.status_code
        self.headers = response.headers
        self.raw_response = response


class WithRawResponse:
    """Proxy that wraps every method call to return RawResponse instead of parsed data."""

    def __init__(self, resource: Any, http: Any) -> None:
        self._resource = resource
        self._http = http

    def __getattr__(self, name: str) -> Any:
        method = getattr(self._resource, name)
        if name.startswith("_") or name == "list":
            return method

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            captured: list[httpx.Response] = []
            original_request = self._http.request

            def capturing_request(*a: Any, **kw: Any) -> Any:
                response = original_request(*a, **kw)
                captured.append(response)
                return response

            self._http.request = capturing_request
            try:
                data = method(*args, **kwargs)
            finally:
                self._http.request = original_request

            if captured:
                return RawResponse(data=data, response=captured[-1])
            return data

        return wrapper


class AsyncWithRawResponse:
    """Async proxy that wraps every method call to return RawResponse."""

    def __init__(self, resource: Any, http: Any) -> None:
        self._resource = resource
        self._http = http

    def __getattr__(self, name: str) -> Any:
        method = getattr(self._resource, name)
        if name.startswith("_") or name == "list":
            return method

        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            captured: list[httpx.Response] = []
            original_request = self._http.request

            async def capturing_request(*a: Any, **kw: Any) -> Any:
                response = await original_request(*a, **kw)
                captured.append(response)
                return response

            self._http.request = capturing_request
            try:
                data = await method(*args, **kwargs)
            finally:
                self._http.request = original_request

            if captured:
                return RawResponse(data=data, response=captured[-1])
            return data

        return wrapper

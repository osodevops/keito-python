from __future__ import annotations

from typing import Generic, TypeVar

import httpx

T = TypeVar("T")


class RawResponse(Generic[T]):
    """Wraps a parsed response with access to the raw httpx response."""

    def __init__(self, *, data: T, response: httpx.Response) -> None:
        self.data = data
        self.status_code = response.status_code
        self.headers = response.headers
        self.raw_response = response

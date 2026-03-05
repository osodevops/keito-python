from __future__ import annotations

from typing import Optional

from keito.core.http_client import AsyncHttpClient, HttpClient
from keito.core.request_options import RequestOptions
from keito.types.user import User


class UsersResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def me(self, *, request_options: Optional[RequestOptions] = None) -> User:
        response = self._http.request("GET", "/api/v2/users/me", request_options=request_options)
        return User.model_validate(response.json())


class AsyncUsersResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def me(self, *, request_options: Optional[RequestOptions] = None) -> User:
        response = await self._http.request("GET", "/api/v2/users/me", request_options=request_options)
        return User.model_validate(response.json())

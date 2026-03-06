from __future__ import annotations

from typing import Any, Optional, cast

from keito.core.http_client import AsyncHttpClient, HttpClient
from keito.core.pagination import AsyncPageIterator, SyncPageIterator
from keito.core.raw_response import AsyncWithRawResponse, WithRawResponse
from keito.core.request_options import RequestOptions
from keito.types.task import Task

_PATH = "/api/v2/tasks"


class TasksResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self.with_raw_response = WithRawResponse(self, http)

    def _fetch_page(
        self, *, params: dict[str, Any], request_options: Optional[RequestOptions] = None
    ) -> dict[str, Any]:
        response = self._http.request("GET", _PATH, params=params, request_options=request_options)
        return cast(dict[str, Any], response.json())

    def list(
        self,
        *,
        is_active: Optional[bool] = None,
        updated_since: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> SyncPageIterator[Task]:
        params: dict[str, Any] = {
            "is_active": is_active,
            "updated_since": updated_since,
            "per_page": per_page,
        }
        if page is not None:
            params["page"] = page

        return SyncPageIterator(
            fetch_page=self._fetch_page,
            params=params,
            item_key="tasks",
            model_cls=Task,
            request_options=request_options,
        )


class AsyncTasksResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http
        self.with_raw_response = AsyncWithRawResponse(self, http)

    async def _fetch_page(
        self, *, params: dict[str, Any], request_options: Optional[RequestOptions] = None
    ) -> dict[str, Any]:
        response = await self._http.request("GET", _PATH, params=params, request_options=request_options)
        return cast(dict[str, Any], response.json())

    def list(
        self,
        *,
        is_active: Optional[bool] = None,
        updated_since: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> AsyncPageIterator[Task]:
        params: dict[str, Any] = {
            "is_active": is_active,
            "updated_since": updated_since,
            "per_page": per_page,
        }
        if page is not None:
            params["page"] = page

        return AsyncPageIterator(
            fetch_page=self._fetch_page,
            params=params,
            item_key="tasks",
            model_cls=Task,
            request_options=request_options,
        )

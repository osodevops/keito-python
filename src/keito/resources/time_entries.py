from __future__ import annotations

from typing import Any, Optional, cast

from keito.core.http_client import AsyncHttpClient, HttpClient
from keito.core.pagination import AsyncPageIterator, SyncPageIterator
from keito.core.raw_response import AsyncWithRawResponse, WithRawResponse
from keito.core.request_options import RequestOptions
from keito.types.common import Source
from keito.types.time_entry import TimeEntry, TimeEntryCreate, TimeEntryUpdate

_PATH = "/api/v2/time_entries"


class TimeEntriesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self.with_raw_response = WithRawResponse(self, http)

    def _fetch_page(
        self,
        *,
        params: dict[str, Any],
        request_options: Optional[RequestOptions] = None,
    ) -> dict[str, Any]:
        response = self._http.request("GET", _PATH, params=params, request_options=request_options)
        return cast(dict[str, Any], response.json())

    def list(
        self,
        *,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        is_billed: Optional[bool] = None,
        is_running: Optional[bool] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        source: Optional[Source] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> SyncPageIterator[TimeEntry]:
        params: dict[str, Any] = {
            "user_id": user_id,
            "client_id": client_id,
            "project_id": project_id,
            "task_id": task_id,
            "is_billed": is_billed,
            "is_running": is_running,
            "from": from_date,
            "to": to_date,
            "updated_since": updated_since,
            "source": source.value if source else None,
            "per_page": per_page,
        }
        if page is not None:
            params["page"] = page

        return SyncPageIterator(
            fetch_page=self._fetch_page,
            params=params,
            item_key="time_entries",
            model_cls=TimeEntry,
            request_options=request_options,
        )

    def create(
        self,
        *,
        project_id: str,
        task_id: str,
        spent_date: str,
        user_id: Optional[str] = None,
        hours: Optional[float] = None,
        notes: Optional[str] = None,
        billable: Optional[bool] = None,
        is_running: Optional[bool] = None,
        started_time: Optional[str] = None,
        ended_time: Optional[str] = None,
        source: Optional[Source] = None,
        metadata: Optional[dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> TimeEntry:
        body = TimeEntryCreate(
            project_id=project_id,
            task_id=task_id,
            spent_date=spent_date,
            user_id=user_id,
            hours=hours,
            notes=notes,
            billable=billable,
            is_running=is_running,
            started_time=started_time,
            ended_time=ended_time,
            source=source,
            metadata=metadata,
        )
        response = self._http.request(
            "POST",
            _PATH,
            json=body.model_dump(exclude_none=True),
            request_options=request_options,
        )
        return TimeEntry.model_validate(response.json())

    def update(
        self,
        id: str,
        *,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        spent_date: Optional[str] = None,
        hours: Optional[float] = None,
        notes: Optional[str] = None,
        billable: Optional[bool] = None,
        started_time: Optional[str] = None,
        ended_time: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> TimeEntry:
        body = TimeEntryUpdate(
            project_id=project_id,
            task_id=task_id,
            spent_date=spent_date,
            hours=hours,
            notes=notes,
            billable=billable,
            started_time=started_time,
            ended_time=ended_time,
            metadata=metadata,
        )
        response = self._http.request(
            "PATCH",
            f"{_PATH}/{id}",
            json=body.model_dump(exclude_none=True),
            request_options=request_options,
        )
        return TimeEntry.model_validate(response.json())

    def delete(
        self,
        id: str,
        *,
        request_options: Optional[RequestOptions] = None,
    ) -> None:
        self._http.request("DELETE", f"{_PATH}/{id}", request_options=request_options)


class AsyncTimeEntriesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http
        self.with_raw_response = AsyncWithRawResponse(self, http)

    async def _fetch_page(
        self,
        *,
        params: dict[str, Any],
        request_options: Optional[RequestOptions] = None,
    ) -> dict[str, Any]:
        response = await self._http.request("GET", _PATH, params=params, request_options=request_options)
        return cast(dict[str, Any], response.json())

    def list(
        self,
        *,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        is_billed: Optional[bool] = None,
        is_running: Optional[bool] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        source: Optional[Source] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> AsyncPageIterator[TimeEntry]:
        params: dict[str, Any] = {
            "user_id": user_id,
            "client_id": client_id,
            "project_id": project_id,
            "task_id": task_id,
            "is_billed": is_billed,
            "is_running": is_running,
            "from": from_date,
            "to": to_date,
            "updated_since": updated_since,
            "source": source.value if source else None,
            "per_page": per_page,
        }
        if page is not None:
            params["page"] = page

        return AsyncPageIterator(
            fetch_page=self._fetch_page,
            params=params,
            item_key="time_entries",
            model_cls=TimeEntry,
            request_options=request_options,
        )

    async def create(
        self,
        *,
        project_id: str,
        task_id: str,
        spent_date: str,
        user_id: Optional[str] = None,
        hours: Optional[float] = None,
        notes: Optional[str] = None,
        billable: Optional[bool] = None,
        is_running: Optional[bool] = None,
        started_time: Optional[str] = None,
        ended_time: Optional[str] = None,
        source: Optional[Source] = None,
        metadata: Optional[dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> TimeEntry:
        body = TimeEntryCreate(
            project_id=project_id,
            task_id=task_id,
            spent_date=spent_date,
            user_id=user_id,
            hours=hours,
            notes=notes,
            billable=billable,
            is_running=is_running,
            started_time=started_time,
            ended_time=ended_time,
            source=source,
            metadata=metadata,
        )
        response = await self._http.request(
            "POST",
            _PATH,
            json=body.model_dump(exclude_none=True),
            request_options=request_options,
        )
        return TimeEntry.model_validate(response.json())

    async def update(
        self,
        id: str,
        *,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        spent_date: Optional[str] = None,
        hours: Optional[float] = None,
        notes: Optional[str] = None,
        billable: Optional[bool] = None,
        started_time: Optional[str] = None,
        ended_time: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> TimeEntry:
        body = TimeEntryUpdate(
            project_id=project_id,
            task_id=task_id,
            spent_date=spent_date,
            hours=hours,
            notes=notes,
            billable=billable,
            started_time=started_time,
            ended_time=ended_time,
            metadata=metadata,
        )
        response = await self._http.request(
            "PATCH",
            f"{_PATH}/{id}",
            json=body.model_dump(exclude_none=True),
            request_options=request_options,
        )
        return TimeEntry.model_validate(response.json())

    async def delete(
        self,
        id: str,
        *,
        request_options: Optional[RequestOptions] = None,
    ) -> None:
        await self._http.request("DELETE", f"{_PATH}/{id}", request_options=request_options)

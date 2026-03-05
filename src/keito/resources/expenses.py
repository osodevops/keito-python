from __future__ import annotations

from typing import Any, Optional

from keito.core.http_client import AsyncHttpClient, HttpClient
from keito.core.pagination import AsyncPageIterator, SyncPageIterator
from keito.core.request_options import RequestOptions
from keito.types.common import Source
from keito.types.expense import Expense, ExpenseCreate

_PATH = "/api/v2/expenses"


class ExpensesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def _fetch_page(
        self, *, params: dict[str, Any], request_options: Optional[RequestOptions] = None
    ) -> dict[str, Any]:
        response = self._http.request("GET", _PATH, params=params, request_options=request_options)
        return response.json()

    def list(
        self,
        *,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
        project_id: Optional[str] = None,
        is_billed: Optional[bool] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        source: Optional[Source] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> SyncPageIterator[Expense]:
        params: dict[str, Any] = {
            "user_id": user_id,
            "client_id": client_id,
            "project_id": project_id,
            "is_billed": is_billed,
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
            item_key="expenses",
            model_cls=Expense,
            request_options=request_options,
        )

    def create(
        self,
        *,
        project_id: str,
        expense_category_id: str,
        spent_date: str,
        total_cost: Optional[float] = None,
        units: Optional[int] = None,
        notes: Optional[str] = None,
        billable: Optional[bool] = None,
        source: Optional[Source] = None,
        metadata: Optional[dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Expense:
        body = ExpenseCreate(
            project_id=project_id,
            expense_category_id=expense_category_id,
            spent_date=spent_date,
            total_cost=total_cost,
            units=units,
            notes=notes,
            billable=billable,
            source=source,
            metadata=metadata,
        )
        response = self._http.request(
            "POST", _PATH, json=body.model_dump(exclude_none=True), request_options=request_options
        )
        return Expense.model_validate(response.json())


class AsyncExpensesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def _fetch_page(
        self, *, params: dict[str, Any], request_options: Optional[RequestOptions] = None
    ) -> dict[str, Any]:
        response = await self._http.request("GET", _PATH, params=params, request_options=request_options)
        return response.json()

    def list(
        self,
        *,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
        project_id: Optional[str] = None,
        is_billed: Optional[bool] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        source: Optional[Source] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> AsyncPageIterator[Expense]:
        params: dict[str, Any] = {
            "user_id": user_id,
            "client_id": client_id,
            "project_id": project_id,
            "is_billed": is_billed,
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
            item_key="expenses",
            model_cls=Expense,
            request_options=request_options,
        )

    async def create(
        self,
        *,
        project_id: str,
        expense_category_id: str,
        spent_date: str,
        total_cost: Optional[float] = None,
        units: Optional[int] = None,
        notes: Optional[str] = None,
        billable: Optional[bool] = None,
        source: Optional[Source] = None,
        metadata: Optional[dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Expense:
        body = ExpenseCreate(
            project_id=project_id,
            expense_category_id=expense_category_id,
            spent_date=spent_date,
            total_cost=total_cost,
            units=units,
            notes=notes,
            billable=billable,
            source=source,
            metadata=metadata,
        )
        response = await self._http.request(
            "POST", _PATH, json=body.model_dump(exclude_none=True), request_options=request_options
        )
        return Expense.model_validate(response.json())

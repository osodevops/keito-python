from __future__ import annotations

import builtins
from typing import Any, Optional

from keito.core.http_client import AsyncHttpClient, HttpClient
from keito.core.pagination import AsyncPageIterator, SyncPageIterator
from keito.core.request_options import RequestOptions
from keito.resources.invoice_messages import (
    AsyncInvoiceMessagesResource,
    InvoiceMessagesResource,
)
from keito.types.common import InvoiceState, PaymentTerm
from keito.types.invoice import Invoice, InvoiceCreate, InvoiceUpdate, LineItemCreate

_PATH = "/api/v2/invoices"


class InvoicesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self.messages = InvoiceMessagesResource(http)

    def _fetch_page(
        self, *, params: dict[str, Any], request_options: Optional[RequestOptions] = None
    ) -> dict[str, Any]:
        response = self._http.request("GET", _PATH, params=params, request_options=request_options)
        return response.json()

    def list(
        self,
        *,
        client_id: Optional[str] = None,
        state: Optional[InvoiceState] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> SyncPageIterator[Invoice]:
        params: dict[str, Any] = {
            "client_id": client_id,
            "state": state.value if state else None,
            "from": from_date,
            "to": to_date,
            "updated_since": updated_since,
            "per_page": per_page,
        }
        if page is not None:
            params["page"] = page

        return SyncPageIterator(
            fetch_page=self._fetch_page,
            params=params,
            item_key="invoices",
            model_cls=Invoice,
            request_options=request_options,
        )

    def get(self, id: str, *, request_options: Optional[RequestOptions] = None) -> Invoice:
        response = self._http.request("GET", f"{_PATH}/{id}", request_options=request_options)
        return Invoice.model_validate(response.json())

    def create(
        self,
        *,
        client_id: str,
        subject: Optional[str] = None,
        issue_date: Optional[str] = None,
        due_date: Optional[str] = None,
        payment_term: Optional[PaymentTerm] = None,
        currency: Optional[str] = None,
        purchase_order: Optional[str] = None,
        tax: Optional[float] = None,
        tax2: Optional[float] = None,
        discount: Optional[float] = None,
        notes: Optional[str] = None,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        line_items: Optional[builtins.list[dict[str, Any]]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Invoice:
        parsed_items = None
        if line_items is not None:
            parsed_items = [LineItemCreate(**item) for item in line_items]

        body = InvoiceCreate(
            client_id=client_id,
            subject=subject,
            issue_date=issue_date,
            due_date=due_date,
            payment_term=payment_term,
            currency=currency,
            purchase_order=purchase_order,
            tax=tax,
            tax2=tax2,
            discount=discount,
            notes=notes,
            period_start=period_start,
            period_end=period_end,
            line_items=parsed_items,
        )
        response = self._http.request(
            "POST", _PATH, json=body.model_dump(exclude_none=True), request_options=request_options
        )
        return Invoice.model_validate(response.json())

    def update(
        self,
        id: str,
        *,
        subject: Optional[str] = None,
        issue_date: Optional[str] = None,
        due_date: Optional[str] = None,
        purchase_order: Optional[str] = None,
        tax: Optional[float] = None,
        tax2: Optional[float] = None,
        discount: Optional[float] = None,
        notes: Optional[str] = None,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Invoice:
        body = InvoiceUpdate(
            subject=subject,
            issue_date=issue_date,
            due_date=due_date,
            purchase_order=purchase_order,
            tax=tax,
            tax2=tax2,
            discount=discount,
            notes=notes,
            period_start=period_start,
            period_end=period_end,
        )
        response = self._http.request(
            "PATCH",
            f"{_PATH}/{id}",
            json=body.model_dump(exclude_none=True),
            request_options=request_options,
        )
        return Invoice.model_validate(response.json())

    def delete(
        self,
        id: str,
        *,
        request_options: Optional[RequestOptions] = None,
    ) -> dict[str, Any]:
        response = self._http.request("DELETE", f"{_PATH}/{id}", request_options=request_options)
        return response.json()


class AsyncInvoicesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http
        self.messages = AsyncInvoiceMessagesResource(http)

    async def _fetch_page(
        self, *, params: dict[str, Any], request_options: Optional[RequestOptions] = None
    ) -> dict[str, Any]:
        response = await self._http.request("GET", _PATH, params=params, request_options=request_options)
        return response.json()

    def list(
        self,
        *,
        client_id: Optional[str] = None,
        state: Optional[InvoiceState] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> AsyncPageIterator[Invoice]:
        params: dict[str, Any] = {
            "client_id": client_id,
            "state": state.value if state else None,
            "from": from_date,
            "to": to_date,
            "updated_since": updated_since,
            "per_page": per_page,
        }
        if page is not None:
            params["page"] = page

        return AsyncPageIterator(
            fetch_page=self._fetch_page,
            params=params,
            item_key="invoices",
            model_cls=Invoice,
            request_options=request_options,
        )

    async def get(self, id: str, *, request_options: Optional[RequestOptions] = None) -> Invoice:
        response = await self._http.request("GET", f"{_PATH}/{id}", request_options=request_options)
        return Invoice.model_validate(response.json())

    async def create(
        self,
        *,
        client_id: str,
        subject: Optional[str] = None,
        issue_date: Optional[str] = None,
        due_date: Optional[str] = None,
        payment_term: Optional[PaymentTerm] = None,
        currency: Optional[str] = None,
        purchase_order: Optional[str] = None,
        tax: Optional[float] = None,
        tax2: Optional[float] = None,
        discount: Optional[float] = None,
        notes: Optional[str] = None,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        line_items: Optional[builtins.list[dict[str, Any]]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Invoice:
        parsed_items = None
        if line_items is not None:
            parsed_items = [LineItemCreate(**item) for item in line_items]

        body = InvoiceCreate(
            client_id=client_id,
            subject=subject,
            issue_date=issue_date,
            due_date=due_date,
            payment_term=payment_term,
            currency=currency,
            purchase_order=purchase_order,
            tax=tax,
            tax2=tax2,
            discount=discount,
            notes=notes,
            period_start=period_start,
            period_end=period_end,
            line_items=parsed_items,
        )
        response = await self._http.request(
            "POST", _PATH, json=body.model_dump(exclude_none=True), request_options=request_options
        )
        return Invoice.model_validate(response.json())

    async def update(
        self,
        id: str,
        *,
        subject: Optional[str] = None,
        issue_date: Optional[str] = None,
        due_date: Optional[str] = None,
        purchase_order: Optional[str] = None,
        tax: Optional[float] = None,
        tax2: Optional[float] = None,
        discount: Optional[float] = None,
        notes: Optional[str] = None,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Invoice:
        body = InvoiceUpdate(
            subject=subject,
            issue_date=issue_date,
            due_date=due_date,
            purchase_order=purchase_order,
            tax=tax,
            tax2=tax2,
            discount=discount,
            notes=notes,
            period_start=period_start,
            period_end=period_end,
        )
        response = await self._http.request(
            "PATCH",
            f"{_PATH}/{id}",
            json=body.model_dump(exclude_none=True),
            request_options=request_options,
        )
        return Invoice.model_validate(response.json())

    async def delete(
        self,
        id: str,
        *,
        request_options: Optional[RequestOptions] = None,
    ) -> dict[str, Any]:
        response = await self._http.request("DELETE", f"{_PATH}/{id}", request_options=request_options)
        return response.json()

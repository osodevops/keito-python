from __future__ import annotations

import builtins
from typing import Any, Optional, cast

from keito.core.http_client import AsyncHttpClient, HttpClient
from keito.core.pagination import AsyncPageIterator, SyncPageIterator
from keito.core.raw_response import AsyncWithRawResponse, WithRawResponse
from keito.core.request_options import RequestOptions
from keito.types.invoice_message import (
    InvoiceMessage,
    InvoiceMessageCreate,
    InvoiceMessageRecipient,
)


class InvoiceMessagesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http
        self.with_raw_response = WithRawResponse(self, http)

    def _fetch_page(
        self,
        *,
        invoice_id: str,
        params: dict[str, Any],
        request_options: Optional[RequestOptions] = None,
    ) -> dict[str, Any]:
        response = self._http.request(
            "GET",
            f"/api/v2/invoices/{invoice_id}/messages",
            params=params,
            request_options=request_options,
        )
        return cast(dict[str, Any], response.json())

    def list(
        self,
        invoice_id: str,
        *,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> SyncPageIterator[InvoiceMessage]:
        params: dict[str, Any] = {"per_page": per_page}
        if page is not None:
            params["page"] = page

        def fetch(*, params: dict[str, Any], request_options: Optional[RequestOptions] = None) -> dict[str, Any]:
            return self._fetch_page(invoice_id=invoice_id, params=params, request_options=request_options)

        return SyncPageIterator(
            fetch_page=fetch,
            params=params,
            item_key="invoice_messages",
            model_cls=InvoiceMessage,
            request_options=request_options,
        )

    def create(
        self,
        invoice_id: str,
        *,
        recipients: builtins.list[dict[str, str]],
        subject: Optional[str] = None,
        body: Optional[str] = None,
        attach_pdf: Optional[bool] = True,
        send_me_a_copy: Optional[bool] = False,
        include_attachments: Optional[bool] = False,
        event_type: Optional[str] = "send",
        request_options: Optional[RequestOptions] = None,
    ) -> InvoiceMessage:
        msg_body = InvoiceMessageCreate(
            recipients=[InvoiceMessageRecipient(**r) for r in recipients],
            subject=subject,
            body=body,
            attach_pdf=attach_pdf,
            send_me_a_copy=send_me_a_copy,
            include_attachments=include_attachments,
            event_type=event_type,
        )
        response = self._http.request(
            "POST",
            f"/api/v2/invoices/{invoice_id}/messages",
            json=msg_body.model_dump(exclude_none=True),
            request_options=request_options,
        )
        return InvoiceMessage.model_validate(response.json())


class AsyncInvoiceMessagesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http
        self.with_raw_response = AsyncWithRawResponse(self, http)

    async def _fetch_page(
        self,
        *,
        invoice_id: str,
        params: dict[str, Any],
        request_options: Optional[RequestOptions] = None,
    ) -> dict[str, Any]:
        response = await self._http.request(
            "GET",
            f"/api/v2/invoices/{invoice_id}/messages",
            params=params,
            request_options=request_options,
        )
        return cast(dict[str, Any], response.json())

    def list(
        self,
        invoice_id: str,
        *,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> AsyncPageIterator[InvoiceMessage]:
        params: dict[str, Any] = {"per_page": per_page}
        if page is not None:
            params["page"] = page

        async def fetch(
            *, params: dict[str, Any], request_options: Optional[RequestOptions] = None
        ) -> dict[str, Any]:
            return await self._fetch_page(invoice_id=invoice_id, params=params, request_options=request_options)

        return AsyncPageIterator(
            fetch_page=fetch,
            params=params,
            item_key="invoice_messages",
            model_cls=InvoiceMessage,
            request_options=request_options,
        )

    async def create(
        self,
        invoice_id: str,
        *,
        recipients: builtins.list[dict[str, str]],
        subject: Optional[str] = None,
        body: Optional[str] = None,
        attach_pdf: Optional[bool] = True,
        send_me_a_copy: Optional[bool] = False,
        include_attachments: Optional[bool] = False,
        event_type: Optional[str] = "send",
        request_options: Optional[RequestOptions] = None,
    ) -> InvoiceMessage:
        msg_body = InvoiceMessageCreate(
            recipients=[InvoiceMessageRecipient(**r) for r in recipients],
            subject=subject,
            body=body,
            attach_pdf=attach_pdf,
            send_me_a_copy=send_me_a_copy,
            include_attachments=include_attachments,
            event_type=event_type,
        )
        response = await self._http.request(
            "POST",
            f"/api/v2/invoices/{invoice_id}/messages",
            json=msg_body.model_dump(exclude_none=True),
            request_options=request_options,
        )
        return InvoiceMessage.model_validate(response.json())

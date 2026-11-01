from __future__ import annotations

from typing import Any, BinaryIO, Literal, Optional, Union, cast
from urllib.parse import quote

from keito.core.http_client import AsyncHttpClient, HttpClient
from keito.core.pagination import AsyncPageIterator, SyncPageIterator
from keito.core.raw_response import AsyncWithRawResponse, WithRawResponse
from keito.core.request_options import RequestOptions
from keito.types.common import ApprovalStatus, Source, SourceParam, source_value
from keito.types.expense import Expense, ExpenseCreate, ExpenseReceipt, ExpenseUpdate

_PATH = "/api/v2/expenses"


def _expense_path(id: str) -> str:
    if not id or not id.strip():
        raise ValueError("expense id must not be blank")
    return f"{_PATH}/{quote(id, safe='')}"


def _receipt_file(file: Union[BinaryIO, bytes], filename: str, content_type: str) -> tuple[str, bytes, str]:
    if not filename or not content_type:
        raise ValueError("Receipt filename and content_type are required")
    limit = 9 * 1024 * 1024
    if isinstance(file, bytes):
        contents = file
    else:
        chunks = []
        size = 0
        while size <= limit:
            chunk = file.read(min(64 * 1024, limit + 1 - size))
            if not isinstance(chunk, bytes):
                raise TypeError("Receipt file must contain bytes")
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
        contents = b"".join(chunks)
    if not isinstance(contents, bytes):
        raise TypeError("Receipt file must contain bytes")
    if not 0 < len(contents) <= limit:
        raise ValueError("Receipt must be non-empty and no larger than 9 MiB")
    return filename, contents, content_type


class ExpensesResource:
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
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
        project_id: Optional[str] = None,
        is_billed: Optional[bool] = None,
        expense_category_id: Optional[str] = None,
        approval_status: Optional[ApprovalStatus] = None,
        invoice_id: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        source: Optional[SourceParam] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> SyncPageIterator[Expense]:
        params: dict[str, Any] = {
            "user_id": user_id,
            "client_id": client_id,
            "project_id": project_id,
            "is_billed": is_billed,
            "expense_category_id": expense_category_id,
            "approval_status": ApprovalStatus(approval_status).value if approval_status is not None else None,
            "invoice_id": invoice_id,
            "from": from_date,
            "to": to_date,
            "updated_since": updated_since,
            "source": source_value(source),
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
        units: Optional[float] = None,
        entry_type: Optional[Literal["expense", "refund"]] = None,
        adjustment_reason: Optional[str] = None,
        adjustment_of_id: Optional[str] = None,
        notes: Optional[str] = None,
        billable: Optional[bool] = None,
        attach_receipt_to_invoice: Optional[bool] = None,
        source: Optional[SourceParam] = None,
        metadata: Optional[dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Expense:
        body = ExpenseCreate(
            project_id=project_id,
            expense_category_id=expense_category_id,
            spent_date=spent_date,
            total_cost=total_cost,
            units=units,
            entry_type=entry_type,
            adjustment_reason=adjustment_reason,
            adjustment_of_id=adjustment_of_id,
            notes=notes,
            billable=billable,
            source=Source(source) if source is not None else None,
            attach_receipt_to_invoice=attach_receipt_to_invoice,
            metadata=metadata,
        )
        response = self._http.request(
            "POST", _PATH, json=body.model_dump(exclude_none=True), request_options=request_options
        )
        return Expense.model_validate(response.json())

    def get(self, id: str, *, request_options: Optional[RequestOptions] = None) -> Expense:
        response = self._http.request("GET", _expense_path(id), request_options=request_options)
        return Expense.model_validate(response.json())

    def update(self, id: str, *, request_options: Optional[RequestOptions] = None, **fields: Any) -> Expense:
        if not fields:
            raise ValueError("At least one expense field is required")
        body = ExpenseUpdate.model_validate(fields)
        response = self._http.request(
            "PATCH",
            _expense_path(id),
            json=body.model_dump(mode="json", exclude_unset=True),
            request_options=request_options,
        )
        return Expense.model_validate(response.json())

    def delete(self, id: str, *, request_options: Optional[RequestOptions] = None) -> None:
        self._http.request("DELETE", _expense_path(id), request_options=request_options)

    def download_receipt(self, id: str, *, request_options: Optional[RequestOptions] = None) -> bytes:
        response = self._http.request("GET", f"{_expense_path(id)}/receipt", request_options=request_options)
        return response.content

    def upload_receipt(
        self,
        id: str,
        *,
        file: Union[BinaryIO, bytes],
        filename: str,
        content_type: str,
        request_options: Optional[RequestOptions] = None,
    ) -> ExpenseReceipt:
        receipt = _receipt_file(file, filename, content_type)
        response = self._http.request(
            "POST",
            f"{_expense_path(id)}/receipt",
            files={"file": receipt},
            request_options=request_options,
        )
        return ExpenseReceipt.model_validate(response.json())

    def delete_receipt(self, id: str, *, request_options: Optional[RequestOptions] = None) -> None:
        self._http.request("DELETE", f"{_expense_path(id)}/receipt", request_options=request_options)


class AsyncExpensesResource:
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
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
        project_id: Optional[str] = None,
        is_billed: Optional[bool] = None,
        expense_category_id: Optional[str] = None,
        approval_status: Optional[ApprovalStatus] = None,
        invoice_id: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        updated_since: Optional[str] = None,
        source: Optional[SourceParam] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> AsyncPageIterator[Expense]:
        params: dict[str, Any] = {
            "user_id": user_id,
            "client_id": client_id,
            "project_id": project_id,
            "is_billed": is_billed,
            "expense_category_id": expense_category_id,
            "approval_status": ApprovalStatus(approval_status).value if approval_status is not None else None,
            "invoice_id": invoice_id,
            "from": from_date,
            "to": to_date,
            "updated_since": updated_since,
            "source": source_value(source),
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
        units: Optional[float] = None,
        entry_type: Optional[Literal["expense", "refund"]] = None,
        adjustment_reason: Optional[str] = None,
        adjustment_of_id: Optional[str] = None,
        notes: Optional[str] = None,
        billable: Optional[bool] = None,
        attach_receipt_to_invoice: Optional[bool] = None,
        source: Optional[SourceParam] = None,
        metadata: Optional[dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Expense:
        body = ExpenseCreate(
            project_id=project_id,
            expense_category_id=expense_category_id,
            spent_date=spent_date,
            total_cost=total_cost,
            units=units,
            entry_type=entry_type,
            adjustment_reason=adjustment_reason,
            adjustment_of_id=adjustment_of_id,
            notes=notes,
            billable=billable,
            source=Source(source) if source is not None else None,
            attach_receipt_to_invoice=attach_receipt_to_invoice,
            metadata=metadata,
        )
        response = await self._http.request(
            "POST", _PATH, json=body.model_dump(exclude_none=True), request_options=request_options
        )
        return Expense.model_validate(response.json())

    async def get(self, id: str, *, request_options: Optional[RequestOptions] = None) -> Expense:
        response = await self._http.request("GET", _expense_path(id), request_options=request_options)
        return Expense.model_validate(response.json())

    async def update(self, id: str, *, request_options: Optional[RequestOptions] = None, **fields: Any) -> Expense:
        if not fields:
            raise ValueError("At least one expense field is required")
        body = ExpenseUpdate.model_validate(fields)
        response = await self._http.request(
            "PATCH",
            _expense_path(id),
            json=body.model_dump(mode="json", exclude_unset=True),
            request_options=request_options,
        )
        return Expense.model_validate(response.json())

    async def delete(self, id: str, *, request_options: Optional[RequestOptions] = None) -> None:
        await self._http.request("DELETE", _expense_path(id), request_options=request_options)

    async def download_receipt(self, id: str, *, request_options: Optional[RequestOptions] = None) -> bytes:
        response = await self._http.request("GET", f"{_expense_path(id)}/receipt", request_options=request_options)
        return response.content

    async def upload_receipt(
        self,
        id: str,
        *,
        file: Union[BinaryIO, bytes],
        filename: str,
        content_type: str,
        request_options: Optional[RequestOptions] = None,
    ) -> ExpenseReceipt:
        receipt = _receipt_file(file, filename, content_type)
        response = await self._http.request(
            "POST",
            f"{_expense_path(id)}/receipt",
            files={"file": receipt},
            request_options=request_options,
        )
        return ExpenseReceipt.model_validate(response.json())

    async def delete_receipt(self, id: str, *, request_options: Optional[RequestOptions] = None) -> None:
        await self._http.request("DELETE", f"{_expense_path(id)}/receipt", request_options=request_options)

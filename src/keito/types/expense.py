from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, field_validator

from keito.types.common import ApprovalStatus, IdName, Source


class Expense(BaseModel):
    model_config = {"frozen": True}

    id: str
    user_id: str
    project_id: str
    expense_category_id: str
    user: IdName
    project: IdName
    expense_category: IdName
    spent_date: date
    total_cost: float
    units: Optional[float] = None
    currency: Optional[str] = None
    entry_type: Literal["expense", "refund"] = "expense"
    adjustment_reason: Optional[str] = None
    adjustment_of_id: Optional[str] = None
    notes: Optional[str] = None
    billable: bool = False
    receipt_file_name: Optional[str] = None
    receipt_file_size: Optional[int] = None
    receipt_content_type: Optional[str] = None
    receipt_url: Optional[str] = None
    attach_receipt_to_invoice: bool = False
    invoice_id: Optional[str] = None
    is_locked: bool = False
    is_billed: bool = False
    approval_status: Optional[ApprovalStatus] = None
    source: Source
    metadata: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class ExpenseCreate(BaseModel):
    project_id: str
    expense_category_id: str
    spent_date: str
    total_cost: Optional[float] = None
    units: Optional[float] = None
    entry_type: Optional[Literal["expense", "refund"]] = None
    adjustment_reason: Optional[str] = None
    adjustment_of_id: Optional[str] = None
    notes: Optional[str] = None
    billable: Optional[bool] = None
    attach_receipt_to_invoice: Optional[bool] = None
    source: Optional[Source] = None
    metadata: Optional[dict[str, Any]] = None


class ExpenseUpdate(BaseModel):
    """Writable fields; exclude_unset preserves explicit null when updating."""

    model_config = {"extra": "forbid"}

    project_id: Optional[str] = None
    expense_category_id: Optional[str] = None
    spent_date: Optional[str] = None
    total_cost: Optional[float] = None
    units: Optional[float] = None
    adjustment_reason: Optional[str] = None
    notes: Optional[str] = None
    billable: Optional[bool] = None
    attach_receipt_to_invoice: Optional[bool] = None
    metadata: Optional[dict[str, Any]] = None

    @field_validator(
        "project_id", "expense_category_id", "spent_date", "adjustment_reason", "billable", "attach_receipt_to_invoice"
    )
    @classmethod
    def reject_null_for_non_nullable_fields(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("This expense field cannot be null")
        return value


class ExpenseReceipt(BaseModel):
    model_config = {"frozen": True}

    receipt_file_name: Optional[str] = None
    receipt_file_size: Optional[int] = None
    receipt_content_type: Optional[str] = None
    receipt_url: str

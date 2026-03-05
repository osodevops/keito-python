from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel

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
    units: Optional[int] = None
    notes: Optional[str] = None
    billable: bool = False
    receipt_file_name: Optional[str] = None
    receipt_content_type: Optional[str] = None
    receipt_url: Optional[str] = None
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
    units: Optional[int] = None
    notes: Optional[str] = None
    billable: Optional[bool] = None
    source: Optional[Source] = None
    metadata: Optional[dict[str, Any]] = None

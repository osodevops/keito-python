from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from keito.types.common import IdName


class Project(BaseModel):
    model_config = {"frozen": True}

    id: str
    client: Optional[IdName] = None
    name: str
    code: Optional[str] = None
    is_active: bool = True
    is_billable: bool = False
    is_fixed_fee: bool = False
    bill_by: Optional[str] = None
    hourly_rate: Optional[float] = None
    fee: Optional[float] = None
    budget_by: Optional[str] = None
    budget: Optional[float] = None
    budget_is_monthly: bool = False
    notify_when_over_budget: bool = False
    over_budget_notification_percentage: Optional[float] = None
    show_budget_to_all: bool = False
    cost_budget: Optional[float] = None
    cost_budget_include_expenses: bool = False
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

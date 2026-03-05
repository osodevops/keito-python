from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from keito.types.common import IdName, Source


class TimeEntry(BaseModel):
    model_config = {"frozen": True}

    id: str
    user_id: str
    project_id: str
    task_id: str
    user: IdName
    project: IdName
    task: IdName
    spent_date: date
    hours: float
    notes: Optional[str] = None
    is_running: bool = False
    timer_started_at: Optional[datetime] = None
    started_time: Optional[str] = None
    ended_time: Optional[str] = None
    is_locked: bool = False
    is_closed: bool = False
    is_billed: bool = False
    billable: bool = False
    budgeted: bool = False
    billable_rate: Optional[float] = None
    cost_rate: Optional[float] = None
    source: Source
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class TimeEntryCreate(BaseModel):
    project_id: str
    task_id: str
    spent_date: str
    user_id: Optional[str] = None
    hours: Optional[float] = None
    notes: Optional[str] = None
    billable: Optional[bool] = None
    is_running: Optional[bool] = None
    started_time: Optional[str] = None
    ended_time: Optional[str] = None
    source: Optional[Source] = None
    metadata: Optional[Dict[str, Any]] = None


class TimeEntryUpdate(BaseModel):
    project_id: Optional[str] = None
    task_id: Optional[str] = None
    spent_date: Optional[str] = None
    hours: Optional[float] = None
    notes: Optional[str] = None
    billable: Optional[bool] = None
    started_time: Optional[str] = None
    ended_time: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

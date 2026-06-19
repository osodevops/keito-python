from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, field_validator

from keito.types.common import IdName, Source

_TIME_OF_DAY_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


def _validate_time_of_day(value: Optional[str]) -> Optional[str]:
    if value is None:
        return value
    if not _TIME_OF_DAY_RE.fullmatch(value):
        raise ValueError("time-of-day fields must use HH:mm in the workspace timezone")
    return value


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
    metadata: Optional[dict[str, Any]] = None
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
    replace_running: Optional[bool] = None
    started_time: Optional[str] = None
    ended_time: Optional[str] = None
    source: Optional[Source] = None
    metadata: Optional[dict[str, Any]] = None

    _time_of_day = field_validator("started_time", "ended_time")(_validate_time_of_day)


class TimeEntryUpdate(BaseModel):
    project_id: Optional[str] = None
    task_id: Optional[str] = None
    spent_date: Optional[str] = None
    hours: Optional[float] = None
    notes: Optional[str] = None
    billable: Optional[bool] = None
    started_time: Optional[str] = None
    ended_time: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

    _time_of_day = field_validator("started_time", "ended_time")(_validate_time_of_day)

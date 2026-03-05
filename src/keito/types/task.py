from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Task(BaseModel):
    model_config = {"frozen": True}

    id: str
    name: str
    billable_by_default: bool = False
    default_hourly_rate: Optional[float] = None
    is_default: bool = False
    is_active: bool = True
    parent_task_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TeamTimeResult(BaseModel):
    model_config = {"frozen": True}

    user_id: str
    user_name: Optional[str] = None
    is_contractor: bool = False
    weekly_capacity: Optional[int] = None
    avatar_url: Optional[str] = None
    total_hours: float = 0
    billable_hours: float = 0
    currency: Optional[str] = None
    billable_amount: float = 0

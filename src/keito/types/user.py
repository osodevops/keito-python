from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from keito.types.common import IdName, UserType


class User(BaseModel):
    model_config = {"frozen": True}

    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    telephone: Optional[str] = None
    timezone: Optional[str] = None
    has_access_to_all_future_projects: bool = False
    is_contractor: bool = False
    is_active: bool = True
    weekly_capacity: Optional[int] = None
    default_hourly_rate: Optional[float] = None
    cost_rate: Optional[float] = None
    currency: Optional[str] = None
    roles: List[str] = []
    user_type: Optional[UserType] = None
    avatar_url: Optional[str] = None
    company: Optional[IdName] = None
    created_at: datetime
    updated_at: datetime

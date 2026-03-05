from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from keito.types.common import IdName


class Contact(BaseModel):
    model_config = {"frozen": True}

    id: str
    client: Optional[IdName] = None
    first_name: str
    last_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone_office: Optional[str] = None
    phone_mobile: Optional[str] = None
    fax: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ContactCreate(BaseModel):
    client_id: str
    first_name: str
    last_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone_office: Optional[str] = None
    phone_mobile: Optional[str] = None
    fax: Optional[str] = None

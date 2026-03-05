from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from keito.types.common import PaymentTerm


class ClientModel(BaseModel):
    model_config = {"frozen": True}

    id: str
    name: str
    address: Optional[str] = None
    currency: Optional[str] = None
    is_active: bool = True
    payment_terms: Optional[str] = None
    payment_days: Optional[int] = None
    tax: Optional[float] = None
    tax2: Optional[float] = None
    discount: Optional[float] = None
    statement_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ClientCreate(BaseModel):
    name: str
    address: Optional[str] = None
    currency: Optional[str] = None
    payment_terms: Optional[PaymentTerm] = None
    payment_days: Optional[int] = None
    tax: Optional[float] = None
    tax2: Optional[float] = None
    discount: Optional[float] = None
    is_active: Optional[bool] = None

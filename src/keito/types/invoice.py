from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from keito.types.common import IdName, InvoiceState, PaymentTerm


class LineItem(BaseModel):
    model_config = {"frozen": True}

    id: Optional[str] = None
    kind: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    taxed: bool = False
    taxed2: bool = False
    project_id: Optional[str] = None


class InvoiceCreator(BaseModel):
    model_config = {"frozen": True}

    id: str
    name: Optional[str] = None
    email: Optional[str] = None


class Invoice(BaseModel):
    model_config = {"frozen": True}

    id: str
    client_id: str
    created_by_id: Optional[str] = None
    client: Optional[IdName] = None
    creator: Optional[InvoiceCreator] = None
    number: Optional[str] = None
    purchase_order: Optional[str] = None
    subject: Optional[str] = None
    state: Optional[InvoiceState] = None
    amount: Optional[float] = None
    due_amount: Optional[float] = None
    tax: Optional[float] = None
    tax_amount: Optional[float] = None
    tax2: Optional[float] = None
    tax2_amount: Optional[float] = None
    discount: Optional[float] = None
    discount_amount: Optional[float] = None
    currency: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    payment_term: Optional[PaymentTerm] = None
    notes: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    sent_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    line_items: list[LineItem] = []


class LineItemCreate(BaseModel):
    kind: Optional[str] = "Service"
    description: Optional[str] = None
    quantity: Optional[float] = 1
    unit_price: Optional[float] = 0
    taxed: Optional[bool] = False
    taxed2: Optional[bool] = False
    project_id: Optional[str] = None


class InvoiceCreate(BaseModel):
    client_id: str
    subject: Optional[str] = None
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    payment_term: Optional[PaymentTerm] = None
    currency: Optional[str] = None
    purchase_order: Optional[str] = None
    tax: Optional[float] = None
    tax2: Optional[float] = None
    discount: Optional[float] = None
    notes: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    line_items: Optional[list[LineItemCreate]] = None


class InvoiceUpdate(BaseModel):
    subject: Optional[str] = None
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    purchase_order: Optional[str] = None
    tax: Optional[float] = None
    tax2: Optional[float] = None
    discount: Optional[float] = None
    notes: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None

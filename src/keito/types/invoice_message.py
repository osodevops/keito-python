from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class InvoiceMessageRecipient(BaseModel):
    name: str
    email: str


class InvoiceMessage(BaseModel):
    model_config = {"frozen": True}

    id: str
    invoice_id: str
    sent_by: Optional[str] = None
    sent_by_email: Optional[str] = None
    sent_from: Optional[str] = None
    sent_from_email: Optional[str] = None
    recipients: Optional[Any] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    attach_pdf: bool = False
    send_me_a_copy: bool = False
    thank_you: bool = False
    reminder: bool = False
    event_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class InvoiceMessageCreate(BaseModel):
    recipients: list[InvoiceMessageRecipient]
    subject: Optional[str] = None
    body: Optional[str] = None
    attach_pdf: Optional[bool] = True
    send_me_a_copy: Optional[bool] = False
    include_attachments: Optional[bool] = False
    event_type: Optional[str] = "send"

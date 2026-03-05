from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class Source(str, Enum):
    WEB = "web"
    CLI = "cli"
    API = "api"
    AGENT = "agent"


class UserType(str, Enum):
    HUMAN = "human"
    AGENT = "agent"


class PaymentTerm(str, Enum):
    UPON_RECEIPT = "upon_receipt"
    NET_15 = "net_15"
    NET_30 = "net_30"
    NET_45 = "net_45"
    NET_60 = "net_60"
    CUSTOM = "custom"


class InvoiceState(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    CLOSED = "closed"


class ApprovalStatus(str, Enum):
    UNSUBMITTED = "unsubmitted"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class IdName(BaseModel):
    model_config = {"frozen": True}

    id: str
    name: Optional[str] = None


Metadata = Optional[Dict[str, Any]]

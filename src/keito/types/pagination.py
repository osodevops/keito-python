from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PaginationLinks(BaseModel):
    model_config = {"frozen": True}

    first: Optional[str] = None
    next: Optional[str] = None
    previous: Optional[str] = None
    last: Optional[str] = None


class PaginationEnvelope(BaseModel):
    model_config = {"frozen": True}

    per_page: Optional[int] = None
    total_pages: Optional[int] = None
    total_entries: Optional[int] = None
    page: Optional[int] = None
    links: Optional[PaginationLinks] = None

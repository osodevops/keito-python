from __future__ import annotations

from typing import Any, Dict, Optional

from typing_extensions import TypedDict


class RequestOptions(TypedDict, total=False):
    timeout: Optional[float]
    max_retries: Optional[int]
    additional_headers: Optional[Dict[str, Any]]

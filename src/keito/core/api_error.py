from __future__ import annotations

from typing import Any, Optional

import httpx


class KeitoApiError(Exception):
    """Base error for all Keito API errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        body: Optional[dict[str, Any]] = None,
        headers: Optional[httpx.Headers] = None,
        raw_response: Optional[httpx.Response] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body
        self.headers = headers
        self.raw_response = raw_response

    def __str__(self) -> str:
        msg = f"[{self.status_code}]"
        if self.body:
            error = self.body.get("error", "")
            desc = self.body.get("error_description", "")
            if error:
                msg += f" {error}"
            if desc:
                msg += f": {desc}"
        else:
            msg += f" {super().__str__()}"
        return msg


class KeitoAuthError(KeitoApiError):
    """401 Unauthorized."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__("Unauthorized", status_code=401, **kwargs)


class KeitoForbiddenError(KeitoApiError):
    """403 Forbidden."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__("Forbidden", status_code=403, **kwargs)


class KeitoNotFoundError(KeitoApiError):
    """404 Not Found."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__("Not Found", status_code=404, **kwargs)


class KeitoValidationError(KeitoApiError):
    """400 Bad Request."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__("Bad Request", status_code=400, **kwargs)


class KeitoConflictError(KeitoApiError):
    """409 Conflict."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__("Conflict", status_code=409, **kwargs)


class KeitoRateLimitError(KeitoApiError):
    """429 Too Many Requests."""

    retry_after: Optional[float]

    def __init__(self, *, retry_after: Optional[float] = None, **kwargs: Any) -> None:
        super().__init__("Rate Limited", status_code=429, **kwargs)
        self.retry_after = retry_after


class KeitoServerError(KeitoApiError):
    """5xx Server Error."""

    def __init__(self, status_code: int = 500, **kwargs: Any) -> None:
        super().__init__("Server Error", status_code=status_code, **kwargs)


class KeitoTimeoutError(Exception):
    """Request timed out."""

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message)


class KeitoConnectionError(Exception):
    """Network connection error."""

    def __init__(self, message: str = "Connection error") -> None:
        super().__init__(message)

import pytest
from pytest_httpx import HTTPXMock

from keito import (
    Keito,
    KeitoAuthError,
    KeitoConflictError,
    KeitoForbiddenError,
    KeitoNotFoundError,
    KeitoRateLimitError,
    KeitoValidationError,
)

_BASE = "https://app.keito.io/api/v2/time_entries"


def test_401_raises_auth_error(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        status_code=401,
        json={"error": "unauthorized", "error_description": "Invalid API key"},
    )

    with pytest.raises(KeitoAuthError) as exc_info:
        client.time_entries.create(
            project_id="p", task_id="t", spent_date="2026-01-01", hours=1
        )
    assert exc_info.value.status_code == 401


def test_403_raises_forbidden_error(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        status_code=403,
        json={"error": "forbidden", "error_description": "Insufficient permissions"},
    )

    with pytest.raises(KeitoForbiddenError):
        client.time_entries.create(
            project_id="p", task_id="t", spent_date="2026-01-01", hours=1
        )


def test_404_raises_not_found_error(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        status_code=404,
        json={"error": "not_found"},
    )

    with pytest.raises(KeitoNotFoundError):
        client.time_entries.update("nonexistent", hours=1)


def test_409_raises_conflict_error(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        status_code=409,
        json={"error": "conflict", "error_description": "Entry is approved"},
    )

    with pytest.raises(KeitoConflictError) as exc_info:
        client.time_entries.delete("entry_locked")
    assert exc_info.value.body["error_description"] == "Entry is approved"


def test_400_raises_validation_error(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        status_code=400,
        json={"error": "bad_request", "error_description": "project_id is required"},
    )

    with pytest.raises(KeitoValidationError):
        client.time_entries.create(
            project_id="", task_id="t", spent_date="2026-01-01"
        )


def test_429_raises_rate_limit_error(httpx_mock: HTTPXMock):
    # Need max_retries=0 to avoid retries on 429
    client = Keito(api_key="kto_test", account_id="acc_test", max_retries=0)
    httpx_mock.add_response(
        status_code=429,
        json={"error": "rate_limited"},
        headers={"Retry-After": "2"},
    )

    with pytest.raises(KeitoRateLimitError) as exc_info:
        client.users.me()
    assert exc_info.value.retry_after == 2.0


def test_missing_api_key_raises_auth_error():
    import os

    env_backup = os.environ.get("KEITO_API_KEY")
    os.environ.pop("KEITO_API_KEY", None)
    os.environ.pop("KEITO_ACCOUNT_ID", None)

    try:
        with pytest.raises(KeitoAuthError):
            Keito()
    finally:
        if env_backup:
            os.environ["KEITO_API_KEY"] = env_backup


def test_missing_account_id_raises_auth_error():
    with pytest.raises(KeitoAuthError):
        Keito(api_key="kto_test")

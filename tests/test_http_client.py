"""Tests for HTTP client edge cases, error formatting, and async retry paths."""

import pytest
from pytest_httpx import HTTPXMock

from keito import (
    AsyncKeito,
    Keito,
    KeitoApiError,
    KeitoAuthError,
    KeitoConnectionError,
    KeitoRateLimitError,
    KeitoServerError,
    KeitoTimeoutError,
)

_BASE = "https://app.keito.io/api/v2"

_USER_JSON = {
    "id": "user_123",
    "email": "test@example.com",
    "is_active": True,
    "roles": [],
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}


# --- Error __str__ ---

def test_api_error_str_with_body():
    err = KeitoAuthError(body={"error": "unauthorized", "error_description": "Invalid token"})
    s = str(err)
    assert "401" in s
    assert "unauthorized" in s
    assert "Invalid token" in s


def test_api_error_str_without_body():
    err = KeitoApiError("Something went wrong", status_code=418)
    s = str(err)
    assert "418" in s
    assert "Something went wrong" in s


def test_api_error_str_with_error_only():
    err = KeitoServerError(body={"error": "internal_error"})
    s = str(err)
    assert "500" in s
    assert "internal_error" in s


def test_rate_limit_error_no_retry_after():
    err = KeitoRateLimitError(body={"error": "rate_limited"})
    assert err.retry_after is None
    assert err.status_code == 429


def test_timeout_error():
    err = KeitoTimeoutError("timed out after 60s")
    assert "timed out" in str(err)


def test_connection_error():
    err = KeitoConnectionError("refused")
    assert "refused" in str(err)


# --- Unexpected status code ---

def test_unexpected_status_code(httpx_mock: HTTPXMock):
    client = Keito(api_key="kto_test", account_id="acc_test", max_retries=0)
    httpx_mock.add_response(status_code=418, json={"error": "teapot"})

    with pytest.raises(KeitoApiError) as exc_info:
        client.users.me()
    assert exc_info.value.status_code == 418


# --- Server error with non-json body ---

def test_server_error_non_json_body(httpx_mock: HTTPXMock):
    client = Keito(api_key="kto_test", account_id="acc_test", max_retries=0)
    httpx_mock.add_response(status_code=502, text="Bad Gateway")

    with pytest.raises(KeitoServerError) as exc_info:
        client.users.me()
    assert exc_info.value.body is None


# --- 429 with Retry-After header (retry path) ---

def test_retry_after_header_respected(httpx_mock: HTTPXMock):
    client = Keito(api_key="kto_test", account_id="acc_test", max_retries=1)

    httpx_mock.add_response(status_code=429, headers={"Retry-After": "0"})
    httpx_mock.add_response(json=_USER_JSON)

    user = client.users.me()
    assert user.id == "user_123"
    assert len(httpx_mock.get_requests()) == 2


# --- Async retries ---

@pytest.mark.asyncio
async def test_async_retries_on_500(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test", max_retries=1)

    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(json=_USER_JSON)

    user = await client.users.me()
    assert user.id == "user_123"
    assert len(httpx_mock.get_requests()) == 2
    await client.close()


@pytest.mark.asyncio
async def test_async_exhausted_retries(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test", max_retries=1)

    httpx_mock.add_response(status_code=500)
    httpx_mock.add_response(status_code=500)

    with pytest.raises(KeitoServerError):
        await client.users.me()
    await client.close()


@pytest.mark.asyncio
async def test_async_no_retry_on_post(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test", max_retries=2)

    httpx_mock.add_response(status_code=500)

    with pytest.raises(KeitoServerError):
        await client.time_entries.create(
            project_id="p", task_id="t", spent_date="2026-01-01", hours=1
        )

    assert len(httpx_mock.get_requests()) == 1
    await client.close()


@pytest.mark.asyncio
async def test_async_429_retry(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test", max_retries=1)

    httpx_mock.add_response(status_code=429, headers={"Retry-After": "0"})
    httpx_mock.add_response(json=_USER_JSON)

    user = await client.users.me()
    assert user.id == "user_123"
    await client.close()


# --- Custom httpx client ---

def test_custom_httpx_client(httpx_mock: HTTPXMock):
    import httpx

    custom = httpx.Client()
    client = Keito(api_key="kto_test", account_id="acc_test", httpx_client=custom)
    httpx_mock.add_response(method="GET", url=f"{_BASE}/users/me", json=_USER_JSON)

    user = client.users.me()
    assert user.id == "user_123"
    # Should not close custom client
    client.close()
    assert not custom.is_closed
    custom.close()


# --- Bring-your-own async client ---

@pytest.mark.asyncio
async def test_custom_async_httpx_client(httpx_mock: HTTPXMock):
    import httpx

    custom = httpx.AsyncClient()
    client = AsyncKeito(api_key="kto_test", account_id="acc_test", httpx_client=custom)
    httpx_mock.add_response(method="GET", url=f"{_BASE}/users/me", json=_USER_JSON)

    user = await client.users.me()
    assert user.id == "user_123"
    await client.close()
    assert not custom.is_closed
    await custom.aclose()


# --- Sync invoice message list ---

def test_invoice_messages_list(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        json={
            "invoice_messages": [
                {
                    "id": "msg_1",
                    "invoice_id": "inv_1",
                    "sent_by": "User",
                    "sent_by_email": "u@e.com",
                    "subject": "Invoice",
                    "attach_pdf": True,
                    "send_me_a_copy": False,
                    "thank_you": False,
                    "reminder": False,
                    "event_type": "send",
                    "created_at": "2026-03-05T10:00:00Z",
                    "updated_at": "2026-03-05T10:00:00Z",
                }
            ],
            "per_page": 100,
            "total_pages": 1,
            "total_entries": 1,
        },
    )

    messages = list(client.invoices.messages.list("inv_1"))
    assert len(messages) == 1
    assert messages[0].id == "msg_1"


# --- Client update with payment_terms enum ---

def test_client_update_with_payment_terms(httpx_mock: HTTPXMock, client: Keito):
    from keito.types.common import PaymentTerm

    httpx_mock.add_response(
        method="PATCH",
        url=f"{_BASE}/clients/cli_123",
        json={
            "id": "cli_123",
            "name": "Acme",
            "is_active": True,
            "currency": "GBP",
            "payment_terms": "net_30",
            "created_at": "2026-03-05T10:00:00Z",
            "updated_at": "2026-03-05T10:00:00Z",
        },
    )

    result = client.clients.update("cli_123", payment_terms=PaymentTerm.NET_30, tax=10.0, tax2=5.0, discount=2.0)
    assert result.id == "cli_123"

    import json
    request = httpx_mock.get_request()
    body = json.loads(request.content)
    assert body["payment_terms"] == "net_30"
    assert body["tax"] == 10.0

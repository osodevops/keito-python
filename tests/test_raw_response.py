import pytest
from pytest_httpx import HTTPXMock

from keito import AsyncKeito, Keito
from keito.core.raw_response import RawResponse
from keito.types import TimeEntry, User

_BASE = "https://app.keito.io/api/v2"

_ENTRY_JSON = {
    "id": "entry_123",
    "user_id": "user_456",
    "project_id": "proj_789",
    "task_id": "task_012",
    "user": {"id": "user_456", "name": "Test User"},
    "project": {"id": "proj_789", "name": "Test Project"},
    "task": {"id": "task_012", "name": "Development"},
    "spent_date": "2026-03-05",
    "hours": 1.5,
    "notes": "Test entry",
    "is_running": False,
    "is_locked": False,
    "is_closed": False,
    "is_billed": False,
    "billable": True,
    "budgeted": False,
    "source": "api",
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}

_USER_JSON = {
    "id": "user_123",
    "email": "test@example.com",
    "is_active": True,
    "roles": [],
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}


def test_with_raw_response_create(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/time_entries",
        json=_ENTRY_JSON,
        status_code=201,
    )

    result = client.time_entries.with_raw_response.create(
        project_id="proj_789",
        task_id="task_012",
        spent_date="2026-03-05",
        hours=1.5,
    )

    assert isinstance(result, RawResponse)
    assert isinstance(result.data, TimeEntry)
    assert result.data.id == "entry_123"
    assert result.status_code == 201
    assert result.raw_response is not None


def test_with_raw_response_me(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/users/me",
        json=_USER_JSON,
    )

    result = client.users.with_raw_response.me()

    assert isinstance(result, RawResponse)
    assert isinstance(result.data, User)
    assert result.data.id == "user_123"
    assert result.status_code == 200
    assert result.headers is not None


def test_with_raw_response_update(httpx_mock: HTTPXMock, client: Keito):
    updated = {**_ENTRY_JSON, "notes": "Updated"}
    httpx_mock.add_response(
        method="PATCH",
        url=f"{_BASE}/time_entries/entry_123",
        json=updated,
    )

    result = client.time_entries.with_raw_response.update("entry_123", notes="Updated")

    assert isinstance(result, RawResponse)
    assert result.data.notes == "Updated"


def test_with_raw_response_delete(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        method="DELETE",
        url=f"{_BASE}/time_entries/entry_123",
        status_code=204,
    )

    result = client.time_entries.with_raw_response.delete("entry_123")

    assert isinstance(result, RawResponse)
    assert result.status_code == 204


@pytest.mark.asyncio
async def test_async_with_raw_response_create(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")

    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/time_entries",
        json=_ENTRY_JSON,
        status_code=201,
    )

    result = await client.time_entries.with_raw_response.create(
        project_id="proj_789",
        task_id="task_012",
        spent_date="2026-03-05",
        hours=1.5,
    )

    assert isinstance(result, RawResponse)
    assert isinstance(result.data, TimeEntry)
    assert result.data.id == "entry_123"
    assert result.status_code == 201

    await client.close()


@pytest.mark.asyncio
async def test_async_with_raw_response_me(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")

    httpx_mock.add_response(
        method="GET",
        url=f"{_BASE}/users/me",
        json=_USER_JSON,
    )

    result = await client.users.with_raw_response.me()

    assert isinstance(result, RawResponse)
    assert isinstance(result.data, User)
    assert result.data.id == "user_123"

    await client.close()

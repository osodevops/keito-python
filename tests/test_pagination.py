import pytest
from pytest_httpx import HTTPXMock

from keito import AsyncKeito, Keito
from keito.types import TimeEntry

_BASE = "https://app.keito.io/api/v2/time_entries"

_ENTRY_TEMPLATE = {
    "user_id": "user_1",
    "project_id": "proj_1",
    "task_id": "task_1",
    "user": {"id": "user_1", "name": "User"},
    "project": {"id": "proj_1", "name": "Project"},
    "task": {"id": "task_1", "name": "Task"},
    "spent_date": "2026-03-05",
    "hours": 1.0,
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


def _make_entry(id: str) -> dict:
    return {**_ENTRY_TEMPLATE, "id": id}


def test_sync_pagination_multiple_pages(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        json={
            "time_entries": [_make_entry("e1"), _make_entry("e2")],
            "per_page": 2,
            "total_pages": 3,
            "total_entries": 5,
            "page": 1,
        },
    )
    httpx_mock.add_response(
        json={
            "time_entries": [_make_entry("e3"), _make_entry("e4")],
            "per_page": 2,
            "total_pages": 3,
            "total_entries": 5,
            "page": 2,
        },
    )
    httpx_mock.add_response(
        json={
            "time_entries": [_make_entry("e5")],
            "per_page": 2,
            "total_pages": 3,
            "total_entries": 5,
            "page": 3,
        },
    )

    entries = list(client.time_entries.list(per_page=2))
    assert len(entries) == 5
    assert [e.id for e in entries] == ["e1", "e2", "e3", "e4", "e5"]


def test_sync_pagination_empty_result(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        json={
            "time_entries": [],
            "per_page": 100,
            "total_pages": 0,
            "total_entries": 0,
            "page": 1,
        },
    )

    entries = list(client.time_entries.list())
    assert entries == []


def test_sync_pagination_metadata(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        json={
            "time_entries": [_make_entry("e1")],
            "per_page": 50,
            "total_pages": 1,
            "total_entries": 1,
            "page": 1,
        },
    )

    iterator = client.time_entries.list(per_page=50)
    # Consume first item to trigger page fetch
    first = next(iterator)
    assert first.id == "e1"
    assert iterator.total_entries == 1
    assert iterator.total_pages == 1
    assert iterator.per_page == 50


@pytest.mark.asyncio
async def test_async_pagination(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")

    httpx_mock.add_response(
        json={
            "time_entries": [_make_entry("e1")],
            "per_page": 1,
            "total_pages": 2,
            "total_entries": 2,
            "page": 1,
        },
    )
    httpx_mock.add_response(
        json={
            "time_entries": [_make_entry("e2")],
            "per_page": 1,
            "total_pages": 2,
            "total_entries": 2,
            "page": 2,
        },
    )

    entries = []
    async for entry in client.time_entries.list(per_page=1):
        entries.append(entry)

    assert len(entries) == 2
    assert entries[0].id == "e1"
    assert entries[1].id == "e2"

    await client.close()

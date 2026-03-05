from pytest_httpx import HTTPXMock

from keito import Keito
from keito.types import Source, TimeEntry

_BASE = "https://app.keito.io/api/v2/time_entries"

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
    "timer_started_at": None,
    "started_time": None,
    "ended_time": None,
    "is_locked": False,
    "is_closed": False,
    "is_billed": False,
    "billable": True,
    "budgeted": False,
    "billable_rate": 150.0,
    "cost_rate": None,
    "source": "agent",
    "metadata": {"agent_id": "test-agent"},
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}


def test_create_time_entry(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="POST", url=_BASE, json=_ENTRY_JSON)

    entry = client.time_entries.create(
        project_id="proj_789",
        task_id="task_012",
        spent_date="2026-03-05",
        hours=1.5,
        notes="Test entry",
        source=Source.AGENT,
        metadata={"agent_id": "test-agent"},
    )

    assert isinstance(entry, TimeEntry)
    assert entry.id == "entry_123"
    assert entry.source == Source.AGENT
    assert entry.hours == 1.5
    assert entry.billable is True


def test_update_time_entry(httpx_mock: HTTPXMock, client: Keito):
    updated = {**_ENTRY_JSON, "notes": "Updated notes", "hours": 2.0}
    httpx_mock.add_response(method="PATCH", url=f"{_BASE}/entry_123", json=updated)

    entry = client.time_entries.update("entry_123", notes="Updated notes", hours=2.0)

    assert entry.notes == "Updated notes"
    assert entry.hours == 2.0


def test_delete_time_entry(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="DELETE", url=f"{_BASE}/entry_123", status_code=204)

    client.time_entries.delete("entry_123")


def test_list_time_entries(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        method="GET",
        json={
            "time_entries": [_ENTRY_JSON],
            "per_page": 100,
            "total_pages": 1,
            "total_entries": 1,
            "page": 1,
        },
    )

    entries = list(client.time_entries.list(source=Source.AGENT))
    assert len(entries) == 1
    assert entries[0].id == "entry_123"


def test_list_time_entries_pagination(httpx_mock: HTTPXMock, client: Keito):
    entry2 = {**_ENTRY_JSON, "id": "entry_456"}

    httpx_mock.add_response(
        method="GET",
        json={
            "time_entries": [_ENTRY_JSON],
            "per_page": 1,
            "total_pages": 2,
            "total_entries": 2,
            "page": 1,
        },
    )
    httpx_mock.add_response(
        method="GET",
        json={
            "time_entries": [entry2],
            "per_page": 1,
            "total_pages": 2,
            "total_entries": 2,
            "page": 2,
        },
    )

    entries = list(client.time_entries.list(per_page=1))
    assert len(entries) == 2
    assert entries[0].id == "entry_123"
    assert entries[1].id == "entry_456"


def test_create_sends_correct_headers(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="POST", url=_BASE, json=_ENTRY_JSON)

    client.time_entries.create(
        project_id="proj_789",
        task_id="task_012",
        spent_date="2026-03-05",
        hours=1.5,
    )

    request = httpx_mock.get_request()
    assert request.headers["Authorization"] == "Bearer kto_test_key"
    assert request.headers["Keito-Account-Id"] == "acc_test_123"
    assert "keito-python/" in request.headers["User-Agent"]

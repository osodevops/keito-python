"""Tests for clients, contacts, projects, tasks, reports, and users resources."""

import pytest
from pytest_httpx import HTTPXMock

from keito import AsyncKeito, Keito
from keito.types import ClientModel, Contact, Project, Task, TeamTimeResult, User

_BASE = "https://app.keito.io/api/v2"

_CLIENT_JSON = {
    "id": "cli_123",
    "name": "Acme Corp",
    "is_active": True,
    "currency": "GBP",
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}

_CONTACT_JSON = {
    "id": "con_123",
    "client_id": "cli_123",
    "client": {"id": "cli_123", "name": "Acme Corp"},
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@acme.com",
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}

_PROJECT_JSON = {
    "id": "proj_123",
    "client_id": "cli_123",
    "client": {"id": "cli_123", "name": "Acme Corp"},
    "name": "Project Alpha",
    "code": "PA",
    "is_active": True,
    "is_billable": True,
    "bill_by": "Tasks",
    "budget_by": "project",
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}

_TASK_JSON = {
    "id": "task_123",
    "name": "Development",
    "is_active": True,
    "is_default": False,
    "billable_by_default": True,
    "default_hourly_rate": 150.0,
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}

_TEAM_TIME_JSON = {
    "user_id": "user_123",
    "user_name": "Test Agent",
    "billable_hours": 42.0,
    "billable_amount": 6300.0,
    "total_hours": 45.0,
}

_USER_JSON = {
    "id": "user_123",
    "email": "test@example.com",
    "is_active": True,
    "roles": ["admin"],
    "first_name": "Test",
    "last_name": "User",
    "user_type": "human",
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}


# --- Clients ---

def test_create_client(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="POST", url=f"{_BASE}/clients", json=_CLIENT_JSON)

    result = client.clients.create(name="Acme Corp")
    assert isinstance(result, ClientModel)
    assert result.id == "cli_123"
    assert result.name == "Acme Corp"


def test_get_client(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="GET", url=f"{_BASE}/clients/cli_123", json=_CLIENT_JSON)

    result = client.clients.get("cli_123")
    assert result.id == "cli_123"


def test_update_client(httpx_mock: HTTPXMock, client: Keito):
    updated = {**_CLIENT_JSON, "name": "Acme Inc"}
    httpx_mock.add_response(method="PATCH", url=f"{_BASE}/clients/cli_123", json=updated)

    result = client.clients.update("cli_123", name="Acme Inc")
    assert result.name == "Acme Inc"


def test_list_clients(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        json={
            "clients": [_CLIENT_JSON],
            "per_page": 100,
            "total_pages": 1,
            "total_entries": 1,
        },
    )

    results = list(client.clients.list())
    assert len(results) == 1
    assert results[0].id == "cli_123"


# --- Contacts ---

def test_create_contact(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="POST", url=f"{_BASE}/contacts", json=_CONTACT_JSON)

    result = client.contacts.create(client_id="cli_123", first_name="John", last_name="Doe", email="john@acme.com")
    assert isinstance(result, Contact)
    assert result.first_name == "John"


def test_list_contacts(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        json={
            "contacts": [_CONTACT_JSON],
            "per_page": 100,
            "total_pages": 1,
            "total_entries": 1,
        },
    )

    results = list(client.contacts.list(client_id="cli_123"))
    assert len(results) == 1


# --- Projects ---

def test_list_projects(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        json={
            "projects": [_PROJECT_JSON],
            "per_page": 100,
            "total_pages": 1,
            "total_entries": 1,
        },
    )

    results = list(client.projects.list(is_active=True))
    assert len(results) == 1
    assert isinstance(results[0], Project)
    assert results[0].name == "Project Alpha"


# --- Tasks ---

def test_list_tasks(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        json={
            "tasks": [_TASK_JSON],
            "per_page": 100,
            "total_pages": 1,
            "total_entries": 1,
        },
    )

    results = list(client.tasks.list(is_active=True))
    assert len(results) == 1
    assert isinstance(results[0], Task)
    assert results[0].name == "Development"


# --- Reports ---

def test_team_time_report(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        json={
            "results": [_TEAM_TIME_JSON],
            "per_page": 100,
            "total_pages": 1,
            "total_entries": 1,
        },
    )

    results = list(client.reports.team_time(from_date="20260301", to_date="20260331"))
    assert len(results) == 1
    assert isinstance(results[0], TeamTimeResult)
    assert results[0].billable_hours == 42.0


# --- Users ---

def test_users_me(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="GET", url=f"{_BASE}/users/me", json=_USER_JSON)

    result = client.users.me()
    assert isinstance(result, User)
    assert result.id == "user_123"
    assert result.email == "test@example.com"


# --- Async variants ---

@pytest.mark.asyncio
async def test_async_create_time_entry(httpx_mock: HTTPXMock):
    from keito.types import TimeEntry

    client = AsyncKeito(api_key="kto_test", account_id="acc_test")
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/time_entries",
        json={
            "id": "entry_123",
            "user_id": "user_456",
            "project_id": "proj_789",
            "task_id": "task_012",
            "user": {"id": "user_456", "name": "User"},
            "project": {"id": "proj_789", "name": "Project"},
            "task": {"id": "task_012", "name": "Task"},
            "spent_date": "2026-03-05",
            "hours": 1.5,
            "is_running": False,
            "is_locked": False,
            "is_closed": False,
            "is_billed": False,
            "billable": True,
            "budgeted": False,
            "source": "api",
            "created_at": "2026-03-05T10:00:00Z",
            "updated_at": "2026-03-05T10:00:00Z",
        },
    )

    entry = await client.time_entries.create(
        project_id="proj_789", task_id="task_012", spent_date="2026-03-05", hours=1.5
    )
    assert isinstance(entry, TimeEntry)
    assert entry.id == "entry_123"
    await client.close()


@pytest.mark.asyncio
async def test_async_update_time_entry(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")
    httpx_mock.add_response(
        method="PATCH",
        url=f"{_BASE}/time_entries/entry_123",
        json={
            "id": "entry_123",
            "user_id": "user_456",
            "project_id": "proj_789",
            "task_id": "task_012",
            "user": {"id": "user_456", "name": "User"},
            "project": {"id": "proj_789", "name": "Project"},
            "task": {"id": "task_012", "name": "Task"},
            "spent_date": "2026-03-05",
            "hours": 2.0,
            "notes": "Updated",
            "is_running": False,
            "is_locked": False,
            "is_closed": False,
            "is_billed": False,
            "billable": True,
            "budgeted": False,
            "source": "api",
            "created_at": "2026-03-05T10:00:00Z",
            "updated_at": "2026-03-05T10:00:00Z",
        },
    )

    entry = await client.time_entries.update("entry_123", hours=2.0, notes="Updated")
    assert entry.hours == 2.0
    await client.close()


@pytest.mark.asyncio
async def test_async_delete_time_entry(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")
    httpx_mock.add_response(method="DELETE", url=f"{_BASE}/time_entries/entry_123", status_code=204)

    await client.time_entries.delete("entry_123")
    await client.close()


@pytest.mark.asyncio
async def test_async_users_me(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")
    httpx_mock.add_response(method="GET", url=f"{_BASE}/users/me", json=_USER_JSON)

    result = await client.users.me()
    assert isinstance(result, User)
    assert result.id == "user_123"
    await client.close()


@pytest.mark.asyncio
async def test_async_create_expense(httpx_mock: HTTPXMock):
    from keito.types import Expense

    client = AsyncKeito(api_key="kto_test", account_id="acc_test")
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/expenses",
        json={
            "id": "exp_123",
            "user_id": "user_456",
            "project_id": "proj_789",
            "expense_category_id": "cat_1",
            "user": {"id": "user_456", "name": "User"},
            "project": {"id": "proj_789", "name": "Project"},
            "expense_category": {"id": "cat_1", "name": "Compute"},
            "spent_date": "2026-03-05",
            "total_cost": 0.50,
            "billable": True,
            "is_locked": False,
            "is_billed": False,
            "source": "agent",
            "created_at": "2026-03-05T10:00:00Z",
            "updated_at": "2026-03-05T10:00:00Z",
        },
    )

    expense = await client.expenses.create(
        project_id="proj_789", expense_category_id="cat_1", spent_date="2026-03-05", total_cost=0.50
    )
    assert isinstance(expense, Expense)
    assert expense.total_cost == 0.50
    await client.close()


@pytest.mark.asyncio
async def test_async_create_invoice(httpx_mock: HTTPXMock):
    from keito.types import Invoice

    client = AsyncKeito(api_key="kto_test", account_id="acc_test")
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/invoices",
        json={
            "id": "inv_123",
            "client_id": "cli_789",
            "created_by_id": "user_456",
            "client": {"id": "cli_789", "name": "Client"},
            "creator": {"id": "user_456", "name": "User", "email": "u@e.com"},
            "number": "INV-001",
            "state": "draft",
            "amount": 150.0,
            "due_amount": 150.0,
            "currency": "GBP",
            "issue_date": "2026-03-05",
            "due_date": "2026-04-04",
            "payment_term": "net_30",
            "line_items": [],
            "created_at": "2026-03-05T10:00:00Z",
            "updated_at": "2026-03-05T10:00:00Z",
        },
    )

    invoice = await client.invoices.create(client_id="cli_789", subject="Test")
    assert isinstance(invoice, Invoice)
    assert invoice.id == "inv_123"
    await client.close()


@pytest.mark.asyncio
async def test_async_context_manager(httpx_mock: HTTPXMock):
    httpx_mock.add_response(method="GET", url=f"{_BASE}/users/me", json=_USER_JSON)

    async with AsyncKeito(api_key="kto_test", account_id="acc_test") as client:
        result = await client.users.me()
        assert result.id == "user_123"


def test_sync_context_manager(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="GET", url=f"{_BASE}/users/me", json=_USER_JSON)

    with Keito(api_key="kto_test", account_id="acc_test") as c:
        result = c.users.me()
        assert result.id == "user_123"


def test_request_options(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="GET", url=f"{_BASE}/users/me", json=_USER_JSON)

    result = client.users.me(
        request_options={"timeout": 120.0, "additional_headers": {"X-Custom": "value"}}
    )
    assert result.id == "user_123"

    request = httpx_mock.get_request()
    assert request.headers["X-Custom"] == "value"

"""Async resource tests for coverage of async code paths."""

import pytest
from pytest_httpx import HTTPXMock

from keito import AsyncKeito, OutcomeTypes
from keito.types import ClientModel, Contact, Invoice, InvoiceMessage, Project, Task, TeamTimeResult

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

_INVOICE_JSON = {
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
}

_MESSAGE_JSON = {
    "id": "msg_123",
    "invoice_id": "inv_123",
    "sent_by": "Test User",
    "sent_by_email": "test@example.com",
    "subject": "Invoice",
    "attach_pdf": True,
    "send_me_a_copy": False,
    "thank_you": False,
    "reminder": False,
    "event_type": "send",
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}

_ENTRY_JSON = {
    "id": "entry_123",
    "user_id": "user_456",
    "project_id": "proj_789",
    "task_id": "task_012",
    "user": {"id": "user_456", "name": "Agent"},
    "project": {"id": "proj_789", "name": "Support"},
    "task": {"id": "task_012", "name": "Tickets"},
    "spent_date": "2026-03-05",
    "hours": 0,
    "notes": "Resolved ticket",
    "is_running": False,
    "is_locked": False,
    "is_closed": False,
    "is_billed": False,
    "billable": True,
    "budgeted": False,
    "source": "agent",
    "metadata": {"outcome_type": "ticket_resolved"},
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}


@pytest.mark.asyncio
async def test_async_clients_crud(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")

    # Create
    httpx_mock.add_response(method="POST", url=f"{_BASE}/clients", json=_CLIENT_JSON)
    result = await client.clients.create(name="Acme Corp")
    assert isinstance(result, ClientModel)

    # Get
    httpx_mock.add_response(method="GET", url=f"{_BASE}/clients/cli_123", json=_CLIENT_JSON)
    result = await client.clients.get("cli_123")
    assert result.id == "cli_123"

    # Update
    httpx_mock.add_response(method="PATCH", url=f"{_BASE}/clients/cli_123", json={**_CLIENT_JSON, "name": "Updated"})
    result = await client.clients.update("cli_123", name="Updated")
    assert result.name == "Updated"

    # List
    httpx_mock.add_response(json={"clients": [_CLIENT_JSON], "per_page": 100, "total_pages": 1, "total_entries": 1})
    results = []
    async for c in client.clients.list():
        results.append(c)
    assert len(results) == 1

    await client.close()


@pytest.mark.asyncio
async def test_async_contacts(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")

    httpx_mock.add_response(method="POST", url=f"{_BASE}/contacts", json=_CONTACT_JSON)
    result = await client.contacts.create(client_id="cli_123", first_name="John")
    assert isinstance(result, Contact)

    httpx_mock.add_response(json={"contacts": [_CONTACT_JSON], "per_page": 100, "total_pages": 1, "total_entries": 1})
    results = []
    async for c in client.contacts.list():
        results.append(c)
    assert len(results) == 1

    await client.close()


@pytest.mark.asyncio
async def test_async_projects(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")
    httpx_mock.add_response(
        json={"projects": [_PROJECT_JSON], "per_page": 100, "total_pages": 1, "total_entries": 1}
    )

    results = []
    async for p in client.projects.list():
        results.append(p)
    assert len(results) == 1
    assert isinstance(results[0], Project)
    await client.close()


@pytest.mark.asyncio
async def test_async_tasks(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")
    httpx_mock.add_response(json={"tasks": [_TASK_JSON], "per_page": 100, "total_pages": 1, "total_entries": 1})

    results = []
    async for t in client.tasks.list():
        results.append(t)
    assert len(results) == 1
    assert isinstance(results[0], Task)
    await client.close()


@pytest.mark.asyncio
async def test_async_reports(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")
    httpx_mock.add_response(
        json={"results": [_TEAM_TIME_JSON], "per_page": 100, "total_pages": 1, "total_entries": 1}
    )

    results = []
    async for r in client.reports.team_time(from_date="20260301", to_date="20260331"):
        results.append(r)
    assert len(results) == 1
    assert isinstance(results[0], TeamTimeResult)
    await client.close()


@pytest.mark.asyncio
async def test_async_invoices_full(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")

    # Get
    httpx_mock.add_response(method="GET", url=f"{_BASE}/invoices/inv_123", json=_INVOICE_JSON)
    inv = await client.invoices.get("inv_123")
    assert isinstance(inv, Invoice)

    # Update
    httpx_mock.add_response(method="PATCH", url=f"{_BASE}/invoices/inv_123", json={**_INVOICE_JSON, "subject": "New"})
    inv = await client.invoices.update("inv_123", subject="New")
    assert inv.subject == "New"

    # Delete
    httpx_mock.add_response(method="DELETE", url=f"{_BASE}/invoices/inv_123", json={"deleted": True})
    result = await client.invoices.delete("inv_123")
    assert result["deleted"] is True

    # List
    httpx_mock.add_response(
        json={"invoices": [_INVOICE_JSON], "per_page": 100, "total_pages": 1, "total_entries": 1}
    )
    results = []
    async for i in client.invoices.list():
        results.append(i)
    assert len(results) == 1

    await client.close()


@pytest.mark.asyncio
async def test_async_invoice_messages(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")

    # Create message
    httpx_mock.add_response(method="POST", url=f"{_BASE}/invoices/inv_123/messages", json=_MESSAGE_JSON)
    msg = await client.invoices.messages.create(
        "inv_123", recipients=[{"name": "CFO", "email": "cfo@client.com"}], subject="Invoice"
    )
    assert isinstance(msg, InvoiceMessage)

    # List messages
    httpx_mock.add_response(
        json={"invoice_messages": [_MESSAGE_JSON], "per_page": 100, "total_pages": 1, "total_entries": 1}
    )
    results = []
    async for m in client.invoices.messages.list("inv_123"):
        results.append(m)
    assert len(results) == 1

    await client.close()


@pytest.mark.asyncio
async def test_async_outcomes(httpx_mock: HTTPXMock):
    client = AsyncKeito(api_key="kto_test", account_id="acc_test")
    httpx_mock.add_response(method="POST", url=f"{_BASE}/time_entries", json=_ENTRY_JSON)

    result = await client.outcomes.log(
        project_id="proj_789",
        task_id="task_012",
        spent_date="2026-03-05",
        outcome_type=OutcomeTypes.TICKET_RESOLVED,
        description="Resolved ticket",
        unit_price=0.99,
        success=True,
    )
    assert result.hours == 0
    assert result.source.value == "agent"
    await client.close()

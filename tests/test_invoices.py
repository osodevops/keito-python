from pytest_httpx import HTTPXMock

from keito import Keito
from keito.types import Invoice, InvoiceMessage

_BASE = "https://app.keito.io/api/v2/invoices"

_INVOICE_JSON = {
    "id": "inv_123",
    "client_id": "cli_789",
    "created_by_id": "user_456",
    "client": {"id": "cli_789", "name": "Test Client"},
    "creator": {"id": "user_456", "name": "Test User", "email": "test@example.com"},
    "number": "INV-001",
    "subject": "March 2026 Services",
    "state": "draft",
    "amount": 6300.0,
    "due_amount": 6300.0,
    "currency": "GBP",
    "issue_date": "2026-03-05",
    "due_date": "2026-04-04",
    "payment_term": "net_30",
    "line_items": [
        {
            "id": "li_1",
            "kind": "Service",
            "description": "AI Code Review",
            "quantity": 42,
            "unit_price": 150.0,
            "amount": 6300.0,
            "taxed": False,
            "taxed2": False,
        }
    ],
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}

_MESSAGE_JSON = {
    "id": "msg_123",
    "invoice_id": "inv_123",
    "sent_by": "Test User",
    "sent_by_email": "test@example.com",
    "subject": "Invoice #INV-001",
    "body": "Please find attached.",
    "attach_pdf": True,
    "send_me_a_copy": False,
    "thank_you": False,
    "reminder": False,
    "event_type": "send",
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}


def test_create_invoice(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="POST", url=_BASE, json=_INVOICE_JSON)

    invoice = client.invoices.create(
        client_id="cli_789",
        subject="March 2026 Services",
        line_items=[
            {"kind": "Service", "description": "AI Code Review", "quantity": 42, "unit_price": 150.0},
        ],
    )

    assert isinstance(invoice, Invoice)
    assert invoice.id == "inv_123"
    assert len(invoice.line_items) == 1
    assert invoice.line_items[0].amount == 6300.0


def test_get_invoice(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="GET", url=f"{_BASE}/inv_123", json=_INVOICE_JSON)

    invoice = client.invoices.get("inv_123")
    assert invoice.id == "inv_123"
    assert invoice.state.value == "draft"


def test_update_invoice(httpx_mock: HTTPXMock, client: Keito):
    updated = {**_INVOICE_JSON, "subject": "Updated Subject"}
    httpx_mock.add_response(method="PATCH", url=f"{_BASE}/inv_123", json=updated)

    invoice = client.invoices.update("inv_123", subject="Updated Subject")
    assert invoice.subject == "Updated Subject"


def test_delete_invoice(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        method="DELETE",
        url=f"{_BASE}/inv_123",
        json={"id": "inv_123", "deleted": True},
    )

    result = client.invoices.delete("inv_123")
    assert result["deleted"] is True


def test_list_invoices(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        method="GET",
        json={
            "invoices": [_INVOICE_JSON],
            "per_page": 100,
            "total_pages": 1,
            "total_entries": 1,
            "page": 1,
        },
    )

    invoices = list(client.invoices.list())
    assert len(invoices) == 1


def test_send_invoice_message(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        method="POST",
        url=f"{_BASE}/inv_123/messages",
        json=_MESSAGE_JSON,
    )

    message = client.invoices.messages.create(
        "inv_123",
        recipients=[{"name": "CFO", "email": "cfo@client.com"}],
        subject="Invoice #INV-001",
        attach_pdf=True,
    )

    assert isinstance(message, InvoiceMessage)
    assert message.id == "msg_123"

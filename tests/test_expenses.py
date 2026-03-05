from pytest_httpx import HTTPXMock

from keito import Keito
from keito.types import Expense, Source

_BASE = "https://app.keito.io/api/v2/expenses"

_EXPENSE_JSON = {
    "id": "exp_123",
    "user_id": "user_456",
    "project_id": "proj_789",
    "expense_category_id": "cat_compute",
    "user": {"id": "user_456", "name": "Test User"},
    "project": {"id": "proj_789", "name": "Test Project"},
    "expense_category": {"id": "cat_compute", "name": "Compute"},
    "spent_date": "2026-03-05",
    "total_cost": 0.18,
    "units": None,
    "notes": "API cost",
    "billable": True,
    "is_locked": False,
    "is_billed": False,
    "approval_status": "unsubmitted",
    "source": "agent",
    "metadata": {"tokens_in": 12500},
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}


def test_create_expense(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(method="POST", url=_BASE, json=_EXPENSE_JSON)

    expense = client.expenses.create(
        project_id="proj_789",
        expense_category_id="cat_compute",
        spent_date="2026-03-05",
        total_cost=0.18,
        source=Source.AGENT,
    )

    assert isinstance(expense, Expense)
    assert expense.id == "exp_123"
    assert expense.total_cost == 0.18


def test_list_expenses(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        method="GET",
        json={
            "expenses": [_EXPENSE_JSON],
            "per_page": 100,
            "total_pages": 1,
            "total_entries": 1,
            "page": 1,
        },
    )

    expenses = list(client.expenses.list(source=Source.AGENT))
    assert len(expenses) == 1
    assert expenses[0].id == "exp_123"

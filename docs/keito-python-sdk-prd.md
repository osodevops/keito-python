# Keito Python SDK — Product Requirements Document

**Version:** 1.0
**Date:** 5 March 2026
**Author:** OSO Engineering
**Status:** Draft

---

## Executive Summary

This PRD specifies the `keito` Python SDK — a typed, async-first client library published to PyPI that wraps the Keito API v2. The SDK enables both human developers and AI agents to programmatically track billable work (time and outcomes), manage expenses, and generate invoices.

The design directly adopts the patterns established by AgentMail's Fern-generated Python SDK: resource-based client architecture, Pydantic v2 models, dual sync/async clients backed by `httpx`, automatic retries with exponential backoff, typed error hierarchies, auto-pagination iterators, and raw response access. The goal is an SDK that feels as natural to use as the Stripe Python SDK while being purpose-built for agent workflows.

---

## Design Principles

These principles are drawn directly from the AgentMail Python SDK and validated against the Stripe Python SDK and Fern SDK generator best practices:

| # | Principle | Source | Implementation |
|---|-----------|--------|----------------|
| 1 | **Resource-based client** | AgentMail, Stripe | `client.time_entries.create()` not `client.create_time_entry()` |
| 2 | **Pydantic v2 models** | AgentMail (Fern) | All request/response types are Pydantic `BaseModel` subclasses |
| 3 | **Dual sync + async clients** | AgentMail | `Keito` (sync) and `AsyncKeito` (async) classes |
| 4 | **httpx transport** | AgentMail, Fern | `httpx.Client` for sync, `httpx.AsyncClient` for async |
| 5 | **Automatic retries** | AgentMail, Fern, Stripe | Exponential backoff on 408, 429, 5xx; default 2 retries |
| 6 | **Typed error hierarchy** | AgentMail, Fern | `KetoApiError` → `KetoAuthError`, `KetoNotFoundError`, etc. |
| 7 | **Auto-pagination** | Fern, Stripe, KittyCAD | Sync iterator + async iterator over paginated endpoints |
| 8 | **Raw response access** | AgentMail | `.with_raw_response` property on every resource |
| 9 | **Env var fallback** | AgentMail, Stripe | Read `KEITO_API_KEY` and `KEITO_ACCOUNT_ID` from env |
| 10 | **Frozen models** | Fern default | Response models are immutable after creation |

---

## Build vs. Generate Decision

AgentMail's Python SDK is generated using Fern, as confirmed by its PyPI metadata and `Built with Fern` badge. Fern reads an OpenAPI spec (or Fern Definition) and outputs a complete Python package with Pydantic models, httpx transport, retries, pagination, errors, and auto-generated reference docs.

### Recommendation: Generate with Fern

Given that Keito already has a well-defined OpenAPI v2 spec, Fern generation is the fastest and most maintainable path:

| Factor | Hand-Written | Fern-Generated |
|--------|-------------|----------------|
| **Time to first release** | 3–4 weeks | 3–5 days |
| **API sync risk** | Manual — spec drift possible | Automatic — regenerate on spec change |
| **Maintenance burden** | Every endpoint change requires SDK update | `fern generate` on CI; auto-publish |
| **Code quality** | Varies | Consistent, idiomatic, well-tested patterns |
| **Customisability** | Full control | Custom code via `.fernignore`; extend at will |
| **Type safety** | Manual Pydantic authoring | Auto-generated from spec |
| **Docs** | Manual reference writing | Auto-generated `reference.md` |

If Fern is adopted, the primary engineering work shifts to: (a) enriching the OpenAPI spec with descriptions, examples, and agent-specific documentation, (b) adding custom helper code (e.g., `AgentMetadata`, `outcomes.log()`), and (c) CI/CD pipeline for auto-publishing.

---

## Package Specification

```
Package name:     keito
PyPI:             https://pypi.org/project/keito/
Python versions:  >=3.9, <4.0
License:          MIT
Dependencies:     httpx (>=0.25.0), pydantic (>=2.0), pydantic-core, typing_extensions
Dev dependencies: pytest, pytest-asyncio, pytest-httpx, mypy, ruff, black
Build system:     pyproject.toml + setuptools (or poetry/hatch)
```

---

## Project Structure

```
keito-python/
├── .fern/                          # Fern config (if using Fern)
│   └── generators.yml
├── .fernignore                     # Custom files preserved across regeneration
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Lint, type-check, test
│       └── publish.yml             # Publish to PyPI on tag
├── src/
│   └── keito/
│       ├── __init__.py             # Exports: Keito, AsyncKeito, models, errors
│       ├── client.py               # Keito (sync) and AsyncKeito classes
│       ├── resources/
│       │   ├── __init__.py
│       │   ├── time_entries.py     # TimeEntriesResource, AsyncTimeEntriesResource
│       │   ├── expenses.py
│       │   ├── projects.py
│       │   ├── tasks.py
│       │   ├── clients.py
│       │   ├── contacts.py
│       │   ├── users.py
│       │   ├── invoices.py
│       │   ├── invoice_messages.py
│       │   └── reports.py
│       ├── types/
│       │   ├── __init__.py
│       │   ├── time_entry.py       # TimeEntry, TimeEntryCreate, TimeEntryUpdate
│       │   ├── expense.py
│       │   ├── project.py
│       │   ├── client_model.py     # ClientModel (avoid shadowing `client`)
│       │   ├── contact.py
│       │   ├── task.py
│       │   ├── user.py
│       │   ├── invoice.py
│       │   ├── invoice_message.py
│       │   ├── report.py
│       │   ├── pagination.py       # PaginationEnvelope, PaginationLinks
│       │   ├── error.py            # Error response model
│       │   └── common.py           # IdName, Metadata, Source, UserType enums
│       ├── helpers/
│       │   ├── __init__.py
│       │   ├── agent_metadata.py   # AgentMetadata builder (custom code)
│       │   └── outcomes.py         # Outcome logging convenience (custom code)
│       ├── core/
│       │   ├── __init__.py
│       │   ├── api_error.py        # Error hierarchy
│       │   ├── http_client.py      # httpx wrapper with retries
│       │   ├── pagination.py       # SyncPageIterator, AsyncPageIterator
│       │   ├── raw_response.py     # RawResponse wrapper
│       │   └── request_options.py  # Per-request overrides (timeout, headers)
│       └── _version.py
├── tests/
│   ├── conftest.py
│   ├── test_time_entries.py
│   ├── test_expenses.py
│   ├── test_invoices.py
│   ├── test_pagination.py
│   ├── test_retries.py
│   ├── test_errors.py
│   └── test_helpers.py
├── pyproject.toml
├── README.md
├── reference.md                    # Auto-generated API reference
├── CHANGELOG.md
└── LICENSE
```

---

## Client Architecture

### Initialisation

```python
from keito import Keito, AsyncKeito

# Explicit configuration
client = Keito(
    api_key="kto_...",
    account_id="acc_...",
    base_url="https://app.keito.io",   # optional, default
    timeout=60.0,                       # optional, default 60s
    max_retries=2,                      # optional, default 2
    httpx_client=None,                  # optional, bring your own httpx.Client
)

# Env var fallback (reads KEITO_API_KEY, KEITO_ACCOUNT_ID)
client = Keito()

# Async variant
async_client = AsyncKeito(api_key="kto_...", account_id="acc_...")
```

### Authentication

Every request includes two headers, matching the Keito API v2 spec:

```
Authorization: Bearer kto_...
Keito-Account-Id: <account_cuid>
```

The SDK reads these from constructor args or env vars `KEITO_API_KEY` / `KEITO_ACCOUNT_ID`. If neither is provided, a `KetoAuthError` is raised on client construction.

### Resource Access Pattern

```python
# Resource namespaces mirror API tags
client.time_entries       # TimeEntriesResource
client.expenses           # ExpensesResource
client.projects           # ProjectsResource
client.tasks              # TasksResource
client.clients            # ClientsResource
client.contacts           # ContactsResource
client.users              # UsersResource
client.invoices           # InvoicesResource
client.invoices.messages  # InvoiceMessagesResource (nested)
client.reports            # ReportsResource
```

---

## Resource Methods

### Time Entries

```python
from keito.types import TimeEntry, TimeEntryCreate, TimeEntryUpdate, Source

# Create
entry: TimeEntry = client.time_entries.create(
    project_id="proj_123",
    task_id="task_456",
    spent_date="2026-03-05",
    hours=1.5,
    notes="Automated code review for PR #842",
    source=Source.AGENT,
    billable=True,
    metadata={
        "agent_id": "code-reviewer-v2",
        "run_id": "run_abc123",
        "model": "claude-4-sonnet",
        "tokens_used": 45200,
    },
)

# Get by ID
entry = client.time_entries.get("entry_789")

# Update (merge semantics on metadata)
entry = client.time_entries.update(
    "entry_789",
    notes="Updated review notes",
    metadata={"human_reviewed": True},
)

# Delete
client.time_entries.delete("entry_789")

# List with filters + auto-pagination
for entry in client.time_entries.list(
    source=Source.AGENT,
    project_id="proj_123",
    from_date="2026-03-01",
    to_date="2026-03-31",
):
    print(entry.hours, entry.notes)

# Async list
async for entry in async_client.time_entries.list(source=Source.AGENT):
    print(entry.hours)
```

### Expenses

```python
from keito.types import Expense

expense: Expense = client.expenses.create(
    project_id="proj_123",
    expense_category_id="cat_compute",
    spent_date="2026-03-05",
    total_cost=0.18,
    notes="Claude 4 Sonnet API cost for PR review",
    billable=True,
    source=Source.AGENT,
    metadata={"tokens_in": 12500, "tokens_out": 32700},
)

for expense in client.expenses.list(source=Source.AGENT):
    print(expense.total_cost)
```

### Projects, Tasks, Clients, Contacts, Users

```python
# Read-only for most agent use cases
projects = list(client.projects.list(is_active=True))
project = client.projects.get("proj_123")

tasks = list(client.tasks.list(is_active=True))

clients_list = list(client.clients.list())

me = client.users.me()
print(me.user_type)  # UserType.AGENT
```

### Invoices

```python
from keito.types import Invoice

invoice: Invoice = client.invoices.create(
    client_id="cli_789",
    subject="March 2026 — AI Agent Services",
    period_start="2026-03-01",
    period_end="2026-03-31",
    line_items=[
        {
            "kind": "Service",
            "description": "AI Code Review (42 hours × £150/hr)",
            "quantity": 42,
            "unit_price": 150.00,
        },
        {
            "kind": "Service",
            "description": "312 tickets resolved × £0.99",
            "quantity": 312,
            "unit_price": 0.99,
        },
    ],
)

# Send invoice
message = client.invoices.messages.create(
    invoice.id,
    recipients=[{"name": "Client CFO", "email": "cfo@client.com"}],
    subject="Invoice #INV-2026-042",
    attach_pdf=True,
)
```

### Reports

```python
from keito.types import TeamTimeResult

for result in client.reports.team_time(
    from_date="2026-03-01",
    to_date="2026-03-31",
):
    print(f"{result.user_name}: {result.billable_hours}h (£{result.billable_amount})")
```

---

## Type System

### Pydantic v2 Models

All response types are frozen Pydantic v2 `BaseModel` subclasses. Request types use `TypedDict` for ergonomic keyword arguments.

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum


class Source(str, Enum):
    WEB = "web"
    CLI = "cli"
    API = "api"
    AGENT = "agent"


class UserType(str, Enum):
    HUMAN = "human"
    AGENT = "agent"


class IdName(BaseModel):
    model_config = {"frozen": True}
    id: str
    name: Optional[str] = None


class TimeEntry(BaseModel):
    model_config = {"frozen": True}

    id: str
    user_id: str
    project_id: str
    task_id: str
    user: IdName
    project: IdName
    task: IdName
    spent_date: date
    hours: float
    notes: Optional[str] = None
    is_running: bool
    timer_started_at: Optional[datetime] = None
    started_time: Optional[str] = None
    ended_time: Optional[str] = None
    is_locked: bool
    is_closed: bool
    is_billed: bool
    billable: bool
    budgeted: bool
    billable_rate: Optional[float] = None
    cost_rate: Optional[float] = None
    source: Source
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
```

### Enums

All API enums (`source`, `user_type`, `state`, `payment_terms`, `approval_status`) are represented as Python `str` enums for type safety and autocomplete.

---

## Error Handling

Following the AgentMail pattern, all API errors subclass a base `KetoApiError`:

```python
from keito.core.api_error import (
    KetoApiError,
    KetoAuthError,        # 401
    KetoForbiddenError,   # 403
    KetoNotFoundError,    # 404
    KetoConflictError,    # 409 (locked/approved entries)
    KetoValidationError,  # 400
    KetoRateLimitError,   # 429
    KetoServerError,      # 5xx
)

try:
    client.time_entries.create(...)
except KetoConflictError as e:
    # Entry is approved/locked
    print(e.status_code)  # 409
    print(e.body)         # {"error": "conflict", "error_description": "..."}
except KetoApiError as e:
    print(e.status_code)
    print(e.body)
```

### Error Model

```python
class KetoApiError(Exception):
    status_code: int
    body: Optional[dict]        # Parsed JSON body
    headers: httpx.Headers      # Response headers
    raw_response: httpx.Response
```

---

## Pagination

List endpoints return paginated responses. The SDK provides auto-pagination iterators that handle `page` and `per_page` parameters transparently.

### Sync Iterator

```python
# Iterates through ALL pages automatically
for entry in client.time_entries.list(source=Source.AGENT):
    print(entry.id)

# Get a single page manually
page = client.time_entries.list(source=Source.AGENT, page=1, per_page=50)
print(page.total_entries)
print(page.total_pages)
for entry in page.items:
    print(entry.id)
```

### Async Iterator

```python
async for entry in async_client.time_entries.list(source=Source.AGENT):
    print(entry.id)
```

### Implementation

```python
from typing import TypeVar, Generic, Iterator, AsyncIterator

T = TypeVar("T")

class SyncPageIterator(Generic[T]):
    """Memory-efficient iterator that fetches pages on demand."""

    def __init__(self, fetch_page, params, item_key):
        self._fetch_page = fetch_page
        self._params = params
        self._item_key = item_key
        self._current_page = 0
        self._total_pages = None

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        # Yields individual items, fetching next page when current is exhausted
        ...


class AsyncPageIterator(Generic[T]):
    """Async variant of SyncPageIterator."""

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        ...
```

---

## Retries

The SDK automatically retries failed requests with exponential backoff:

| Parameter | Default | Configurable |
|-----------|---------|-------------|
| Max retries | 2 | `max_retries` on client constructor |
| Backoff base | 0.5s | Internal |
| Backoff max | 8s | Internal |
| Retried status codes | 408, 429, 500, 502, 503, 504 | Internal |
| Retry-After header | Respected if present | Automatic |
| Idempotent methods only | GET, PUT, DELETE always; POST only if idempotency key present | Automatic |

```python
# Override per-client
client = Keito(max_retries=5)

# Override per-request
client.time_entries.create(..., request_options={"max_retries": 0})
```

---

## Raw Response Access

For advanced use cases (inspecting headers, status codes, rate limit info):

```python
response = client.time_entries.with_raw_response.create(
    project_id="proj_123",
    task_id="task_456",
    spent_date="2026-03-05",
    hours=1.5,
)

print(response.status_code)                           # 200
print(response.headers["X-Keito-API-Version"])        # "2"
print(response.headers.get("X-RateLimit-Remaining"))  # "98"

entry: TimeEntry = response.data                      # Parsed Pydantic model
```

---

## Custom Helpers (Non-Generated)

These are custom additions that sit alongside the generated code (preserved via `.fernignore` if using Fern).

### AgentMetadata Builder

```python
from keito.helpers import AgentMetadata

metadata = AgentMetadata.build(
    agent_id="code-reviewer-v2",
    framework="openclaw",
    model_provider="anthropic",
    model_name="claude-4-sonnet",
    tokens_in=12500,
    tokens_out=32700,
    cost_usd=0.18,
    run_id="run_abc123",
    confidence=0.94,
)

# Returns a dict matching the recommended metadata schema:
# {
#   "agent": {"id": "code-reviewer-v2", "framework": "openclaw"},
#   "run": {"id": "run_abc123"},
#   "model": {"provider": "anthropic", "name": "claude-4-sonnet", ...},
#   "quality": {"confidence": 0.94},
# }

entry = client.time_entries.create(
    ...,
    source=Source.AGENT,
    metadata=metadata,
)
```

### Outcome Logging

```python
from keito.helpers.outcomes import OutcomeTypes

# Convenience method that creates a TimeEntry with hours=0 + outcome metadata
outcome = client.outcomes.log(
    project_id="proj_123",
    task_id="task_456",
    spent_date="2026-03-05",
    outcome_type=OutcomeTypes.TICKET_RESOLVED,
    description="Resolved billing inquiry #4821",
    unit_price=0.99,
    quantity=1,
    success=True,
    evidence={"ticket_id": "TKT-4821", "resolution_time": 45},
    metadata=AgentMetadata.build(agent_id="support-agent-v3"),
)
```

---

## Request Options

Every method accepts an optional `request_options` parameter for per-request overrides:

```python
entry = client.time_entries.create(
    ...,
    request_options={
        "timeout": 120.0,
        "max_retries": 0,
        "additional_headers": {"X-Custom-Header": "value"},
    },
)
```

---

## Context Manager Support

Both clients support context manager protocol for proper resource cleanup:

```python
# Sync
with Keito() as client:
    entries = list(client.time_entries.list())

# Async
async with AsyncKeito() as client:
    entries = [e async for e in client.time_entries.list()]
```

---

## Testing Strategy

### Unit Tests

All resource methods are tested against mocked httpx responses using `pytest-httpx`:

```python
import pytest
from pytest_httpx import HTTPXMock
from keito import Keito

def test_create_time_entry(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://app.keito.io/api/v2/time-entries",
        json={
            "id": "entry_123",
            "user_id": "user_456",
            "project_id": "proj_123",
            "task_id": "task_456",
            "spent_date": "2026-03-05",
            "hours": 1.5,
            "source": "agent",
            "billable": True,
            # ... full response
        },
    )

    client = Keito(api_key="kto_test", account_id="acc_test")
    entry = client.time_entries.create(
        project_id="proj_123",
        task_id="task_456",
        spent_date="2026-03-05",
        hours=1.5,
        source="agent",
    )

    assert entry.id == "entry_123"
    assert entry.source == Source.AGENT
    assert entry.hours == 1.5
```

### Test Coverage Targets

| Area | Target |
|------|--------|
| Resource CRUD methods | 100% |
| Pagination | 100% |
| Error handling (all status codes) | 100% |
| Retry logic | 100% |
| Auth (API key, env var, missing) | 100% |
| Custom helpers | 100% |
| Async client parity | 100% |
| Overall line coverage | ≥ 90% |

### CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: mypy src/
      - run: pytest --cov=keito --cov-report=xml
```

### Publish Pipeline

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  push:
    tags: ["v*"]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

---

## pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "keito"
version = "0.1.0"
description = "Python SDK for the Keito time tracking API"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9,<4.0"
authors = [
    {name = "Keito", email = "support@keito.ai"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Typing :: Typed",
]
dependencies = [
    "httpx>=0.25.0",
    "pydantic>=2.0",
    "pydantic-core",
    "typing_extensions>=4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio",
    "pytest-httpx",
    "pytest-cov",
    "mypy",
    "ruff",
    "black",
]

[project.urls]
Homepage = "https://keito.ai"
Documentation = "https://keito.ai/docs"
Repository = "https://github.com/keito-ai/keito-python"
Changelog = "https://github.com/keito-ai/keito-python/blob/main/CHANGELOG.md"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.ruff]
target-version = "py39"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

---

## API Resource Mapping

Complete mapping from Keito API v2 endpoints to SDK methods:

| API Endpoint | HTTP | SDK Method | Returns |
|-------------|------|-----------|---------|
| `GET /api/v2/time-entries` | GET | `client.time_entries.list(...)` | `SyncPageIterator[TimeEntry]` |
| `POST /api/v2/time-entries` | POST | `client.time_entries.create(...)` | `TimeEntry` |
| `PATCH /api/v2/time-entries/{id}` | PATCH | `client.time_entries.update(id, ...)` | `TimeEntry` |
| `DELETE /api/v2/time-entries/{id}` | DELETE | `client.time_entries.delete(id)` | `None` |
| `GET /api/v2/expenses` | GET | `client.expenses.list(...)` | `SyncPageIterator[Expense]` |
| `POST /api/v2/expenses` | POST | `client.expenses.create(...)` | `Expense` |
| `GET /api/v2/projects` | GET | `client.projects.list(...)` | `SyncPageIterator[Project]` |
| `GET /api/v2/projects/{id}` | GET | `client.projects.get(id)` | `Project` |
| `GET /api/v2/clients` | GET | `client.clients.list(...)` | `SyncPageIterator[ClientModel]` |
| `POST /api/v2/clients` | POST | `client.clients.create(...)` | `ClientModel` |
| `GET /api/v2/clients/{id}` | GET | `client.clients.get(id)` | `ClientModel` |
| `PATCH /api/v2/clients/{id}` | PATCH | `client.clients.update(id, ...)` | `ClientModel` |
| `GET /api/v2/contacts` | GET | `client.contacts.list(...)` | `SyncPageIterator[Contact]` |
| `POST /api/v2/contacts` | POST | `client.contacts.create(...)` | `Contact` |
| `GET /api/v2/tasks` | GET | `client.tasks.list(...)` | `SyncPageIterator[Task]` |
| `GET /api/v2/users/me` | GET | `client.users.me()` | `User` |
| `GET /api/v2/invoices` | GET | `client.invoices.list(...)` | `SyncPageIterator[Invoice]` |
| `POST /api/v2/invoices` | POST | `client.invoices.create(...)` | `Invoice` |
| `GET /api/v2/invoices/{id}` | GET | `client.invoices.get(id)` | `Invoice` |
| `PATCH /api/v2/invoices/{id}` | PATCH | `client.invoices.update(id, ...)` | `Invoice` |
| `DELETE /api/v2/invoices/{id}` | DELETE | `client.invoices.delete(id)` | `DeleteResponse` |
| `GET /api/v2/invoices/{id}/messages` | GET | `client.invoices.messages.list(id, ...)` | `SyncPageIterator[InvoiceMessage]` |
| `POST /api/v2/invoices/{id}/messages` | POST | `client.invoices.messages.create(id, ...)` | `InvoiceMessage` |
| `GET /api/v2/reports/time/team` | GET | `client.reports.team_time(...)` | `SyncPageIterator[TeamTimeResult]` |

All `list` methods have corresponding async variants returning `AsyncPageIterator[T]`.

---

## Fern Configuration (If Adopted)

```yaml
# fern/generators.yml
groups:
  python-sdk:
    generators:
      - name: fernapi/fern-python
        version: 4.61.4
        config:
          package_name: "keito"
          client_class_name: "Keito"
          timeout_in_seconds: 60
          pydantic_config:
            version: "v2"
            frozen: true
            skip_validation: false
            use_str_enums: true
            extra_fields: "allow"
        github:
          repository: keito-ai/keito-python
        output:
          location: pypi
          package-name: keito
```

The OpenAPI spec at `openapi-v2.yaml` would be the single source of truth. Running `fern generate` produces the full SDK, and custom code in `src/keito/helpers/` is preserved via `.fernignore`.

---

## Phased Delivery

### Phase 1: Core SDK (Weeks 1–2)

- [ ] Set up Fern config or scaffold hand-written project
- [ ] Generate/implement all resource classes from OpenAPI spec
- [ ] All Pydantic models for request/response types
- [ ] Sync and async clients with httpx transport
- [ ] Auth (API key + account ID, env var fallback)
- [ ] Error hierarchy mapping all API status codes
- [ ] Auto-pagination (sync + async iterators)
- [ ] Retry logic with exponential backoff
- [ ] `pyproject.toml`, CI pipeline, test framework
- [ ] Unit tests for all resources (≥90% coverage)
- [ ] Type checking passes (mypy --strict)

### Phase 2: Helpers & DX (Week 3)

- [ ] `AgentMetadata.build()` helper
- [ ] `outcomes.log()` convenience method
- [ ] `with_raw_response` on all resources
- [ ] Context manager support (`with Keito() as client:`)
- [ ] Request options (per-request timeout, retries, headers)
- [ ] README with quickstart, examples, and agent workflow guide
- [ ] Auto-generated `reference.md`

### Phase 3: Publish & Polish (Week 4)

- [ ] Publish v0.1.0 to PyPI
- [ ] GitHub Actions publish pipeline (tag → PyPI)
- [ ] CHANGELOG.md
- [ ] Integration test suite against staging API
- [ ] Documentation on keito.ai/docs
- [ ] Announce: blog post, GitHub, PyPI

---

## Open Questions

1. **Fern vs hand-written** — Final decision on whether to use Fern generation or hand-write. Recommendation is Fern given the existing OpenAPI spec, but team preference and customisation needs may differ.
2. **Package name** — Is `keito` available on PyPI? If not, alternatives: `keito-sdk`, `keito-python`, `keito-api`.
3. **Python 3.8 support** — AgentMail supports 3.8+, but 3.9+ is recommended for modern typing features. Drop 3.8?
4. **Sync HTTP client** — AgentMail uses httpx for both sync and async. Stripe uses `requests` for sync and `httpx` for async. Recommendation: httpx for both (simpler, one dependency).
5. **Rate limiting** — Does the Keito API enforce rate limits? If so, the SDK should expose rate limit headers and optionally auto-throttle.
6. **Webhook verification** — If Keito adds webhooks, the SDK should include signature verification helpers (Fern supports this).

---

*This PRD is a living document. Last updated: 5 March 2026.*

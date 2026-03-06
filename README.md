# Keito Python SDK

Official Python SDK for the [Keito](https://keito.ai) API — track billable time, expenses, and invoices for humans and AI agents.

[![CI](https://github.com/osodevops/keito-python/actions/workflows/ci.yml/badge.svg)](https://github.com/osodevops/keito-python/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/keito)](https://pypi.org/project/keito/)
[![Python](https://img.shields.io/pypi/pyversions/keito)](https://pypi.org/project/keito/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Features

- **Dual sync + async clients** — `Keito` and `AsyncKeito` backed by `httpx`
- **Typed models** — All responses are frozen Pydantic v2 models with full IDE autocomplete
- **Auto-pagination** — Iterate through all pages with a simple `for` loop
- **Automatic retries** — Exponential backoff on 408, 429, 5xx with jitter
- **Typed error hierarchy** — Catch specific errors like `KeitoNotFoundError` or `KeitoRateLimitError`
- **Agent helpers** — `AgentMetadata.build()` and `outcomes.log()` for AI agent billing workflows
- **Env var fallback** — Reads `KEITO_API_KEY` and `KEITO_ACCOUNT_ID` from environment
- **Context manager support** — Proper resource cleanup with `with` / `async with`

## Installation

```bash
pip install keito
```

Requires Python 3.9+.

## Quick Start

```python
from keito import Keito

# Reads KEITO_API_KEY and KEITO_ACCOUNT_ID from env
client = Keito()

# Or pass explicitly
client = Keito(api_key="kto_...", account_id="acc_...")

# Create a time entry
entry = client.time_entries.create(
    project_id="proj_123",
    task_id="task_456",
    spent_date="2026-03-05",
    hours=1.5,
    notes="Code review for PR #842",
)

# List all time entries (auto-paginates)
for entry in client.time_entries.list(project_id="proj_123"):
    print(f"{entry.spent_date}: {entry.hours}h — {entry.notes}")
```

## Async Usage

```python
from keito import AsyncKeito

async with AsyncKeito() as client:
    entry = await client.time_entries.create(
        project_id="proj_123",
        task_id="task_456",
        spent_date="2026-03-05",
        hours=2.0,
    )

    async for entry in client.time_entries.list():
        print(entry.id)
```

---

## Agent Workflows

The Keito SDK is purpose-built for AI agent billing. Agents can track their own time, log outcome-based events, record LLM costs as expenses, and generate invoices — all programmatically.

### Setting Up an Agent Client

Every Keito agent has its own API key and account. Set these as environment variables in your agent runtime:

```bash
export KEITO_API_KEY="kto_agent_..."
export KEITO_ACCOUNT_ID="acc_..."
```

```python
from keito import Keito
from keito.types import Source

client = Keito()

# Check the agent's identity
me = client.users.me()
print(me.user_type)  # UserType.AGENT
print(me.email)      # agent@yourcompany.com
```

### Tracking Agent Time

Use `source=Source.AGENT` to mark entries as agent-generated. This lets managers filter and report on agent vs. human work.

```python
from keito import Keito, AgentMetadata
from keito.types import Source

client = Keito()

entry = client.time_entries.create(
    project_id="proj_123",
    task_id="task_456",
    spent_date="2026-03-05",
    hours=1.5,
    notes="Automated code review for PR #842",
    source=Source.AGENT,
    billable=True,
    metadata=AgentMetadata.build(
        agent_id="code-reviewer-v2",
        framework="langchain",
        model_provider="anthropic",
        model_name="claude-4-sonnet",
        tokens_in=12500,
        tokens_out=32700,
        cost_usd=0.18,
        run_id="run_abc123",
        confidence=0.94,
    ),
)
```

### Structured Agent Metadata

The `AgentMetadata.build()` helper produces a structured dict following the Keito metadata schema:

```python
from keito import AgentMetadata

metadata = AgentMetadata.build(
    agent_id="support-agent-v3",
    framework="crewai",
    model_provider="anthropic",
    model_name="claude-4-sonnet",
    tokens_in=8000,
    tokens_out=15000,
    cost_usd=0.12,
    run_id="run_xyz",
    parent_run_id="run_parent",
    trigger="webhook",
    confidence=0.97,
    human_reviewed=False,
)

# Produces:
# {
#     "agent": {"id": "support-agent-v3", "framework": "crewai"},
#     "run": {"id": "run_xyz", "parent_id": "run_parent", "trigger": "webhook"},
#     "model": {
#         "provider": "anthropic",
#         "name": "claude-4-sonnet",
#         "tokens_in": 8000,
#         "tokens_out": 15000,
#         "cost_usd": 0.12,
#     },
#     "quality": {"confidence": 0.97, "human_reviewed": False},
# }
```

All fields are optional — include only what's relevant to your agent.

### Outcome-Based Billing

Not all agent work is measured in hours. Use outcomes to bill for discrete events like tickets resolved, leads qualified, or deployments completed.

```python
from keito import Keito, OutcomeTypes

client = Keito()

# Log a resolved ticket as a billable outcome
outcome = client.outcomes.log(
    project_id="proj_123",
    task_id="task_456",
    spent_date="2026-03-05",
    outcome_type=OutcomeTypes.TICKET_RESOLVED,
    description="Resolved billing inquiry #4821",
    unit_price=0.99,
    quantity=1,
    success=True,
    evidence={"ticket_id": "TKT-4821", "resolution_time_seconds": 45},
)

# outcome is a TimeEntry with hours=0, source="agent",
# and metadata containing the outcome details
```

Available outcome types:

| Outcome Type | Value |
|---|---|
| `OutcomeTypes.TICKET_RESOLVED` | `ticket_resolved` |
| `OutcomeTypes.LEAD_QUALIFIED` | `lead_qualified` |
| `OutcomeTypes.CODE_REVIEW_COMPLETED` | `code_review_completed` |
| `OutcomeTypes.PR_MERGED` | `pr_merged` |
| `OutcomeTypes.DEPLOYMENT_COMPLETED` | `deployment_completed` |
| `OutcomeTypes.TEST_SUITE_PASSED` | `test_suite_passed` |
| `OutcomeTypes.DOCUMENT_GENERATED` | `document_generated` |
| `OutcomeTypes.DATA_PIPELINE_RUN` | `data_pipeline_run` |
| `OutcomeTypes.ALERT_TRIAGED` | `alert_triaged` |
| `OutcomeTypes.CUSTOMER_REPLY_SENT` | `customer_reply_sent` |

You can also pass any custom string as `outcome_type` for types not in the enum.

### Logging LLM Costs as Expenses

Track API costs (OpenAI, Anthropic, etc.) as billable expenses:

```python
from keito.types import Source

expense = client.expenses.create(
    project_id="proj_123",
    expense_category_id="cat_llm_api",
    spent_date="2026-03-05",
    total_cost=0.18,
    notes="Claude 4 Sonnet — PR review (12.5k in, 32.7k out)",
    billable=True,
    source=Source.AGENT,
    metadata={
        "model": "claude-4-sonnet",
        "tokens_in": 12500,
        "tokens_out": 32700,
        "provider": "anthropic",
    },
)
```

### Generating Invoices

Agents can create and send invoices for their work:

```python
# Create an invoice with line items
invoice = client.invoices.create(
    client_id="cli_789",
    subject="March 2026 — AI Agent Services",
    period_start="2026-03-01",
    period_end="2026-03-31",
    line_items=[
        {
            "kind": "Service",
            "description": "AI Code Review (42 hours x $150/hr)",
            "quantity": 42,
            "unit_price": 150.00,
        },
        {
            "kind": "Service",
            "description": "312 tickets resolved x $0.99",
            "quantity": 312,
            "unit_price": 0.99,
        },
    ],
)

# Send the invoice via email
message = client.invoices.messages.create(
    invoice.id,
    recipients=[{"name": "Client CFO", "email": "cfo@client.com"}],
    subject=f"Invoice #{invoice.number}",
    attach_pdf=True,
)
```

### Full Agent Loop Example

A complete agent billing loop — track time, log outcomes, record costs, generate invoice:

```python
from keito import Keito, AgentMetadata, OutcomeTypes
from keito.types import Source

client = Keito()

PROJECT = "proj_support"
TASK = "task_tickets"
TODAY = "2026-03-05"

# 1. Track time spent on the run
entry = client.time_entries.create(
    project_id=PROJECT,
    task_id=TASK,
    spent_date=TODAY,
    hours=0.5,
    notes="Support ticket triage batch — 15 tickets processed",
    source=Source.AGENT,
    metadata=AgentMetadata.build(
        agent_id="support-triage-v2",
        model_provider="anthropic",
        model_name="claude-4-sonnet",
        run_id="run_batch_042",
    ),
)

# 2. Log each resolved ticket as an outcome
for ticket_id in ["TKT-101", "TKT-102", "TKT-103"]:
    client.outcomes.log(
        project_id=PROJECT,
        task_id=TASK,
        spent_date=TODAY,
        outcome_type=OutcomeTypes.TICKET_RESOLVED,
        description=f"Resolved {ticket_id}",
        unit_price=0.99,
        success=True,
        evidence={"ticket_id": ticket_id},
    )

# 3. Record LLM API cost
client.expenses.create(
    project_id=PROJECT,
    expense_category_id="cat_llm",
    spent_date=TODAY,
    total_cost=0.42,
    notes="Anthropic API cost for ticket triage batch",
    source=Source.AGENT,
    billable=True,
)

# 4. Query what the agent did today
for e in client.time_entries.list(source=Source.AGENT, from_date=TODAY, to_date=TODAY):
    print(f"  {e.hours}h — {e.notes}")

# 5. Check project and task info
for project in client.projects.list(is_active=True):
    print(f"Project: {project.name} (billable={project.is_billable})")
```

### Filtering Agent Work in Reports

Managers can pull reports filtered to agent activity:

```python
# Team time report — includes both humans and agents
for result in client.reports.team_time(from_date="20260301", to_date="20260331"):
    print(f"{result.user_name}: {result.billable_hours}h (${result.billable_amount})")

# List only agent time entries
for entry in client.time_entries.list(source=Source.AGENT, from_date="2026-03-01"):
    print(f"{entry.user.name}: {entry.hours}h — {entry.notes}")
```

---

## API Reference

### Client Configuration

```python
from keito import Keito, AsyncKeito

client = Keito(
    api_key="kto_...",             # or KEITO_API_KEY env var
    account_id="acc_...",          # or KEITO_ACCOUNT_ID env var
    base_url="https://app.keito.io",  # optional
    timeout=60.0,                  # request timeout in seconds
    max_retries=2,                 # retries on 408/429/5xx
    httpx_client=None,             # bring your own httpx.Client
)
```

### Resources

| Resource | Methods |
|---|---|
| `client.time_entries` | `list()`, `create()`, `update(id)`, `delete(id)` |
| `client.expenses` | `list()`, `create()` |
| `client.projects` | `list()` |
| `client.clients` | `list()`, `create()`, `get(id)`, `update(id)` |
| `client.contacts` | `list()`, `create()` |
| `client.tasks` | `list()` |
| `client.users` | `me()` |
| `client.invoices` | `list()`, `create()`, `get(id)`, `update(id)`, `delete(id)` |
| `client.invoices.messages` | `list(invoice_id)`, `create(invoice_id)` |
| `client.reports` | `team_time(from_date, to_date)` |
| `client.outcomes` | `log()` |

All `list()` methods return auto-paginating iterators. Async variants use `AsyncKeito` and return async iterators.

### Pagination

List methods return iterators that automatically fetch pages:

```python
# Auto-paginate through all results
for entry in client.time_entries.list():
    print(entry.id)

# Access pagination metadata after first iteration
iterator = client.time_entries.list(per_page=50)
first = next(iterator)
print(iterator.total_entries)  # total count across all pages
print(iterator.total_pages)

# Async
async for entry in async_client.time_entries.list():
    print(entry.id)
```

### Error Handling

All API errors are typed and catchable:

```python
from keito import (
    KeitoApiError,         # Base class for all API errors
    KeitoAuthError,        # 401 — invalid or missing credentials
    KeitoForbiddenError,   # 403 — insufficient permissions
    KeitoNotFoundError,    # 404 — resource not found
    KeitoValidationError,  # 400 — invalid request data
    KeitoConflictError,    # 409 — e.g. deleting an approved entry
    KeitoRateLimitError,   # 429 — rate limited (has .retry_after)
    KeitoServerError,      # 5xx — server error
    KeitoTimeoutError,     # request timed out
    KeitoConnectionError,  # network connection failure
)

try:
    client.time_entries.delete("entry_locked")
except KeitoConflictError as e:
    print(e.status_code)  # 409
    print(e.body)         # {"error": "conflict", "error_description": "..."}
except KeitoApiError as e:
    print(e.status_code, e.body)
```

### Retries

Automatic retries with exponential backoff and jitter:

- **Retried status codes:** 408, 429, 500, 502, 503, 504
- **Default retries:** 2 (configurable per-client or per-request)
- **Backoff:** `min(2^(attempt-1) * 0.5s, 8s) + jitter`
- **Retry-After:** Respected on 429 responses
- **POST safety:** POST requests are not retried by default (not idempotent)

```python
# Override per-client
client = Keito(max_retries=5)

# Override per-request
entry = client.time_entries.create(
    ...,
    request_options={"max_retries": 0, "timeout": 120.0},
)
```

### Per-Request Options

Every method accepts `request_options` for per-call overrides:

```python
entry = client.time_entries.create(
    project_id="proj_123",
    task_id="task_456",
    spent_date="2026-03-05",
    hours=1.5,
    request_options={
        "timeout": 120.0,
        "max_retries": 0,
        "additional_headers": {"X-Idempotency-Key": "unique-key-123"},
    },
)
```

### Context Managers

Both clients support proper resource cleanup:

```python
# Sync
with Keito() as client:
    entries = list(client.time_entries.list())

# Async
async with AsyncKeito() as client:
    entries = [e async for e in client.time_entries.list()]
```

---

## Types

All response models are frozen Pydantic v2 `BaseModel` subclasses. Import from `keito.types`:

```python
from keito.types import (
    TimeEntry, TimeEntryCreate, TimeEntryUpdate,
    Expense, ExpenseCreate,
    Project,
    ClientModel, ClientCreate,
    Contact, ContactCreate,
    Task,
    User,
    Invoice, InvoiceCreate, InvoiceUpdate, LineItem,
    InvoiceMessage, InvoiceMessageCreate,
    TeamTimeResult,
    Source, UserType, InvoiceState, PaymentTerm, ApprovalStatus,
    IdName,
)
```

### Enums

```python
from keito.types import Source, UserType, InvoiceState, PaymentTerm, ApprovalStatus

Source.WEB | Source.CLI | Source.API | Source.AGENT
UserType.HUMAN | UserType.AGENT
InvoiceState.DRAFT | InvoiceState.OPEN | InvoiceState.PAID | InvoiceState.CLOSED
PaymentTerm.UPON_RECEIPT | PaymentTerm.NET_15 | PaymentTerm.NET_30 | ...
ApprovalStatus.UNSUBMITTED | ApprovalStatus.SUBMITTED | ApprovalStatus.APPROVED | ApprovalStatus.REJECTED
```

---

## Development

```bash
git clone https://github.com/osodevops/keito-python.git
cd keito-python
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

### Running Tests

```bash
pytest                          # run all tests
pytest --cov=keito              # with coverage
pytest tests/test_retries.py    # single file
ruff check .                    # lint
```

---

## License

MIT

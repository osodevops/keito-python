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
- **Raw response access** — `.with_raw_response` on every resource for headers, status codes, and rate limit info
- **Env var fallback** — Reads `KEITO_API_KEY` and `KEITO_ACCOUNT_ID` from environment
- **Context manager support** — Proper resource cleanup with `with` / `async with`

## Installation

```bash
pip install keito
```

Requires Python 3.9+.

The distribution name is `keito` and the import is `from keito import Keito`.
Use the released package version shown on PyPI; repository-only changes are not
available to installed applications until a release is published.

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

Use `source=Source.API` for ordinary scripted entries. Agent identity and other
context can be recorded as metadata. The `agent` time-entry source is reserved
for Keito's validated lifecycle/public-build metadata contracts; a generic agent
label does not satisfy those contracts.

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
    source=Source.API,
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

Start and stop running timers through the timer helpers. Omit `started_time` when
you want the API to start at the server's current time; `stop_timer()` calculates
elapsed duration server-side.

```python
from datetime import date

timer = client.time_entries.start_timer(
    project_id="proj_123",
    task_id="task_456",
    spent_date=str(date.today()),
    source=Source.API,
    replace_running=True,
)

client.time_entries.stop_timer(timer.id, notes="Finished implementation")
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

### Outcome Metadata

The outcome helper records annotations such as tickets resolved or deployments
completed on a zero-hour time entry. Its price and quantity metadata do not
create an invoice, charge a customer or establish earned revenue. Create any
intended invoice explicitly through the invoice API after review.

```python
from keito import Keito, OutcomeTypes
from keito.types import Source

client = Keito()

# Record a resolved-ticket annotation with a standard API source
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
    source=Source.API,
)

# outcome is a TimeEntry with hours=0, source="api",
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

The helper's historical default remains `Source.AGENT` for compatibility. Pass
`source=Source.API` for ordinary integrations. Applications using the `agent`
source must supply a valid specialized server metadata contract; the helper
does not invent lifecycle evidence or weaken the API's validation.

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
    source=Source.API,
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
    source=Source.API,
    metadata=AgentMetadata.build(
        agent_id="support-triage-v2",
        model_provider="anthropic",
        model_name="claude-4-sonnet",
        run_id="run_batch_042",
    ),
)

# 2. Record outcome annotations; this does not create billed revenue
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
        source=Source.API,
    )

# 3. Record LLM API cost
client.expenses.create(
    project_id=PROJECT,
    expense_category_id="cat_llm",
    spent_date=TODAY,
    total_cost=0.42,
    notes="Anthropic API cost for ticket triage batch",
    source=Source.API,
    billable=True,
)

# 4. Query what the agent did today
for e in client.time_entries.list(source=Source.API, from_date=TODAY, to_date=TODAY):
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
for entry in client.time_entries.list(source=Source.API, from_date="2026-03-01"):
    print(f"{entry.user.name}: {entry.hours}h — {entry.notes}")
```

### Inspecting Rate Limits and Headers

Agents running high-throughput loops should monitor rate limits. Use `.with_raw_response` to inspect headers:

```python
result = client.time_entries.with_raw_response.create(
    project_id=PROJECT,
    task_id=TASK,
    spent_date=TODAY,
    hours=0.5,
    source=Source.API,
)

entry = result.data
remaining = result.headers.get("X-RateLimit-Remaining")
if remaining and int(remaining) < 10:
    print(f"Warning: only {remaining} API calls remaining")
```

---

## API Reference

### Client Configuration

```python
from keito import Keito, AsyncKeito

client = Keito(
    api_key="kto_...",             # or KEITO_API_KEY env var
    account_id="acc_...",          # or KEITO_ACCOUNT_ID env var
    base_url="https://app.keito.ai",  # optional production origin
    timeout=60.0,                  # request timeout in seconds
    max_retries=2,                 # retries on 408/429/5xx
    httpx_client=None,             # bring your own httpx.Client
)
```

`base_url` is an origin, without `/api/v2`; resource methods add that path.
A trailing `/api/v2` is also accepted and normalized, so it is never doubled.
HTTP(S) URLs containing embedded credentials, query strings or fragments are
rejected. Custom origins are intended for your local or staging environment.

### Resources

| Resource | Methods |
|---|---|
| `client.time_entries` | `list()`, `create()`, `start_timer()`, `stop_timer(id)`, `restart_timer(id)`, `update(id)`, `delete(id)` |
| `client.expenses` | `list()`, `create()`, `get(id)`, `update(id)`, `delete(id)`, `upload_receipt(id)`, `download_receipt(id)`, `delete_receipt(id)` |
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

Iterate directly with `for` or `async for`; there is no `.data` page property and
the async `list()` call itself is not awaited. Time and expense source filters
accept a `Source` enum or its string value, for example `Source.AGENT` or `"agent"`.
Invalid source values fail before a request is sent.

### Expense receipts

Create the expense first, retain its ID, and upload the original receipt to that
expense. The category controls whether creation accepts `total_cost` or `units`;
the SDK does not accept a client-supplied `unit_price`. Fractional units are
supported; a returned expense retains `expense.expense_category.unit_price` and
`unit_name` from its category. Ordinary expense create/update supports refund details and
`attach_receipt_to_invoice` under the same rules as the REST API.

```python
expense = client.expenses.create(
    project_id="project_id", expense_category_id="category_id",
    spent_date="2026-10-30", total_cost=24.50,
    request_options={"additional_headers": {"Idempotency-Key": "receipt-expense-001"}},
)
with open("receipt.pdf", "rb") as file:
    receipt = client.expenses.upload_receipt(
        expense.id, file=file, filename="receipt.pdf", content_type="application/pdf",
    )
contents = client.expenses.download_receipt(expense.id)  # bytes
client.expenses.update(expense.id, notes=None)  # explicit null clears notes
```

The upload accepts bytes or a binary file, consumes at most 9 MiB plus a size-check
byte, and returns `ExpenseReceipt` metadata. Use an allowed receipt MIME type:
PDF, JPEG, PNG, GIF, WebP, HEIC, HEIF or TIFF. HTTPX creates the multipart boundary.
Upload is never automatically retried, even if an idempotency header is supplied;
inspect the expense after an uncertain response and keep its ID instead of
creating a duplicate. Approved, billed, locked or inaccessible expenses are still
refused by the server. `delete_receipt(id)` removes the attachment;
`delete(id)` deletes the eligible expense. Both return `None` on success.

Async methods have the same arguments and are awaited, except for the lazy
`list()` iterator. `download_receipt()` returns bytes; use
`with_raw_response.download_receipt()` when you also need its content headers.

The SDK provides no automatic `track_agent_work` context manager or `track`
decorator. Compose explicit timer and expense operations when your application
needs those workflows so its financial and error-handling choices remain clear.

Every resource also exposes `.with_raw_response` for raw `httpx.Response` access (see [Raw Response Access](#raw-response-access)).

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

- **Retried status codes:** 408, 429, 500, 502, 503, 504 for replay-safe requests
- **Default retries:** 2 (configurable per-client or per-request)
- **Backoff:** `min(2^(attempt-1) * 0.5s, 8s) + jitter`
- **Retry-After:** Respected on 429 responses
- **Mutation safety:** POST and PATCH are not retried unless an `Idempotency-Key` is supplied. Use it only on endpoints that support idempotency, and keep its value and request identical when retrying.
- **Receipt safety:** multipart uploads are never retried automatically.

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
        "additional_headers": {"Idempotency-Key": "unique-key-123"},
    },
)
```

### Raw Response Access

Every resource has a `.with_raw_response` property that wraps method calls to return a `RawResponse` object with the parsed data alongside the raw `httpx.Response`. This is useful for inspecting status codes, headers, and rate limit info.

```python
from keito.core.raw_response import RawResponse

# Access raw response alongside parsed data
result = client.time_entries.with_raw_response.create(
    project_id="proj_123",
    task_id="task_456",
    spent_date="2026-03-05",
    hours=1.5,
)

print(result.status_code)        # actual HTTP status returned by the API
print(result.headers)            # httpx.Headers
print(result.raw_response)       # full httpx.Response

entry = result.data              # TimeEntry (parsed Pydantic model)
print(entry.id)

# Works on any resource method (except list)
raw = client.users.with_raw_response.me()
print(raw.data.email)
print(raw.status_code)

# Async variant
result = await async_client.time_entries.with_raw_response.create(...)
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
    Expense, ExpenseCategory, ExpenseCreate, ExpenseUpdate, ExpenseReceipt,
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

Source.WEB | Source.CLI | Source.API | Source.AGENT | Source.CALENDAR | Source.DESKTOP
Source.MOBILE | Source.INTEGRATION | Source.CLICKUP | Source.EXTENSION
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
python -m build                 # builds wheel from the sdist
python scripts/smoke_package.py dist/*.whl  # isolated installed-wheel contract check
```

---

## License

MIT

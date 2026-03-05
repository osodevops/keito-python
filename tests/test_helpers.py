from pytest_httpx import HTTPXMock

from keito import AgentMetadata, Keito, OutcomeTypes
from keito.types import TimeEntry

_ENTRY_JSON = {
    "id": "entry_outcome",
    "user_id": "user_456",
    "project_id": "proj_789",
    "task_id": "task_012",
    "user": {"id": "user_456", "name": "Agent"},
    "project": {"id": "proj_789", "name": "Support"},
    "task": {"id": "task_012", "name": "Tickets"},
    "spent_date": "2026-03-05",
    "hours": 0,
    "notes": "Resolved ticket #4821",
    "is_running": False,
    "is_locked": False,
    "is_closed": False,
    "is_billed": False,
    "billable": True,
    "budgeted": False,
    "source": "agent",
    "metadata": {
        "outcome_type": "ticket_resolved",
        "outcome_quantity": 1,
        "outcome_success": True,
        "outcome_unit_price": 0.99,
    },
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z",
}


def test_agent_metadata_build():
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

    assert metadata["agent"]["id"] == "code-reviewer-v2"
    assert metadata["agent"]["framework"] == "openclaw"
    assert metadata["model"]["provider"] == "anthropic"
    assert metadata["model"]["tokens_in"] == 12500
    assert metadata["run"]["id"] == "run_abc123"
    assert metadata["quality"]["confidence"] == 0.94


def test_agent_metadata_partial():
    metadata = AgentMetadata.build(agent_id="my-agent")
    assert metadata == {"agent": {"id": "my-agent"}}
    assert "model" not in metadata
    assert "run" not in metadata


def test_agent_metadata_empty():
    metadata = AgentMetadata.build()
    assert metadata == {}


def test_outcome_log(httpx_mock: HTTPXMock, client: Keito):
    httpx_mock.add_response(
        method="POST",
        url="https://app.keito.io/api/v2/time_entries",
        json=_ENTRY_JSON,
    )

    outcome = client.outcomes.log(
        project_id="proj_789",
        task_id="task_012",
        spent_date="2026-03-05",
        outcome_type=OutcomeTypes.TICKET_RESOLVED,
        description="Resolved ticket #4821",
        unit_price=0.99,
        quantity=1,
        success=True,
        evidence={"ticket_id": "TKT-4821"},
    )

    assert isinstance(outcome, TimeEntry)
    assert outcome.hours == 0
    assert outcome.source.value == "agent"

    # Verify the request body
    import json

    request = httpx_mock.get_request()
    body = json.loads(request.content)
    assert body["hours"] == 0
    assert body["source"] == "agent"
    assert body["metadata"]["outcome_type"] == "ticket_resolved"
    assert body["metadata"]["outcome_unit_price"] == 0.99
    assert body["metadata"]["outcome_success"] is True


def test_outcome_types_values():
    assert OutcomeTypes.TICKET_RESOLVED.value == "ticket_resolved"
    assert OutcomeTypes.PR_MERGED.value == "pr_merged"
    assert OutcomeTypes.CODE_REVIEW_COMPLETED.value == "code_review_completed"

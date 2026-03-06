from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Union

from keito.types.common import Source
from keito.types.time_entry import TimeEntry

if TYPE_CHECKING:
    from keito.resources.time_entries import AsyncTimeEntriesResource, TimeEntriesResource


class OutcomeTypes(str, Enum):
    TICKET_RESOLVED = "ticket_resolved"
    LEAD_QUALIFIED = "lead_qualified"
    CODE_REVIEW_COMPLETED = "code_review_completed"
    PR_MERGED = "pr_merged"
    DEPLOYMENT_COMPLETED = "deployment_completed"
    TEST_SUITE_PASSED = "test_suite_passed"
    DOCUMENT_GENERATED = "document_generated"
    DATA_PIPELINE_RUN = "data_pipeline_run"
    ALERT_TRIAGED = "alert_triaged"
    CUSTOMER_REPLY_SENT = "customer_reply_sent"


class OutcomesHelper:
    """Sync convenience wrapper for logging outcome-based billing events."""

    def __init__(self, time_entries: TimeEntriesResource) -> None:
        self._time_entries = time_entries

    def log(
        self,
        *,
        project_id: str,
        task_id: str,
        spent_date: str,
        outcome_type: Union[str, OutcomeTypes],
        description: Optional[str] = None,
        unit_price: Optional[float] = None,
        quantity: int = 1,
        success: bool = True,
        evidence: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> TimeEntry:
        outcome_metadata: dict[str, Any] = {
            "outcome_type": outcome_type if isinstance(outcome_type, str) else outcome_type.value,
            "outcome_quantity": quantity,
            "outcome_success": success,
        }
        if unit_price is not None:
            outcome_metadata["outcome_unit_price"] = unit_price
        if evidence is not None:
            outcome_metadata["outcome_evidence"] = evidence

        if metadata:
            outcome_metadata.update(metadata)

        return self._time_entries.create(
            project_id=project_id,
            task_id=task_id,
            spent_date=spent_date,
            hours=0,
            notes=description,
            source=Source.AGENT,
            metadata=outcome_metadata,
        )


class AsyncOutcomesHelper:
    """Async convenience wrapper for logging outcome-based billing events."""

    def __init__(self, time_entries: AsyncTimeEntriesResource) -> None:
        self._time_entries = time_entries

    async def log(
        self,
        *,
        project_id: str,
        task_id: str,
        spent_date: str,
        outcome_type: Union[str, OutcomeTypes],
        description: Optional[str] = None,
        unit_price: Optional[float] = None,
        quantity: int = 1,
        success: bool = True,
        evidence: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> TimeEntry:
        outcome_metadata: dict[str, Any] = {
            "outcome_type": outcome_type if isinstance(outcome_type, str) else outcome_type.value,
            "outcome_quantity": quantity,
            "outcome_success": success,
        }
        if unit_price is not None:
            outcome_metadata["outcome_unit_price"] = unit_price
        if evidence is not None:
            outcome_metadata["outcome_evidence"] = evidence

        if metadata:
            outcome_metadata.update(metadata)

        return await self._time_entries.create(
            project_id=project_id,
            task_id=task_id,
            spent_date=spent_date,
            hours=0,
            notes=description,
            source=Source.AGENT,
            metadata=outcome_metadata,
        )

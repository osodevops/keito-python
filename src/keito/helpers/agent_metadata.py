from __future__ import annotations

from typing import Any, Optional


class AgentMetadata:
    """Builder for structured agent metadata following the Keito metadata schema."""

    @staticmethod
    def build(
        *,
        agent_id: Optional[str] = None,
        framework: Optional[str] = None,
        model_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        tokens_in: Optional[int] = None,
        tokens_out: Optional[int] = None,
        cost_usd: Optional[float] = None,
        run_id: Optional[str] = None,
        parent_run_id: Optional[str] = None,
        trigger: Optional[str] = None,
        confidence: Optional[float] = None,
        human_reviewed: Optional[bool] = None,
    ) -> dict[str, Any]:
        metadata: dict[str, Any] = {}

        # Agent section
        agent: dict[str, Any] = {}
        if agent_id is not None:
            agent["id"] = agent_id
        if framework is not None:
            agent["framework"] = framework
        if agent:
            metadata["agent"] = agent

        # Run section
        run: dict[str, Any] = {}
        if run_id is not None:
            run["id"] = run_id
        if parent_run_id is not None:
            run["parent_id"] = parent_run_id
        if trigger is not None:
            run["trigger"] = trigger
        if run:
            metadata["run"] = run

        # Model section
        model: dict[str, Any] = {}
        if model_provider is not None:
            model["provider"] = model_provider
        if model_name is not None:
            model["name"] = model_name
        if tokens_in is not None:
            model["tokens_in"] = tokens_in
        if tokens_out is not None:
            model["tokens_out"] = tokens_out
        if cost_usd is not None:
            model["cost_usd"] = cost_usd
        if model:
            metadata["model"] = model

        # Quality section
        quality: dict[str, Any] = {}
        if confidence is not None:
            quality["confidence"] = confidence
        if human_reviewed is not None:
            quality["human_reviewed"] = human_reviewed
        if quality:
            metadata["quality"] = quality

        return metadata

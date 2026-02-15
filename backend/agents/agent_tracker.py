"""Tracking system for tool calls in the native Anthropic tool-use architecture.

Records every tool invocation, its result, and which agent domains have completed.
Used by the orchestrator to extract structured data and report errors.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger("itinero.agent_tracker")


@dataclass
class ToolCallRecord:
    """Record of a single tool call."""
    timestamp: str
    tool_name: str
    tool_input: dict[str, Any]
    result_json: Optional[str] = None
    error: Optional[str] = None


class AgentTracker:
    """
    Lightweight tracker for native Anthropic tool-use calls.

    Provides:
    1. Recording of tool calls and their results
    2. Tracking which agent domains have completed
    3. Error collection
    4. Summary generation for the frontend
    """

    def __init__(self) -> None:
        self.tool_call_records: list[ToolCallRecord] = []
        self.agents_completed: set[str] = set()
        self.errors: list[str] = []

        logger.debug("AgentTracker initialized")

    def reset(self) -> None:
        """Clear all records for a fresh turn."""
        self.tool_call_records.clear()
        self.agents_completed.clear()
        self.errors.clear()
        logger.debug("AgentTracker reset")

    def record_tool_call(self, tool_name: str, tool_input: dict) -> ToolCallRecord:
        """Record a new tool call. Returns the record so the caller can set result_json later."""
        record = ToolCallRecord(
            timestamp=datetime.now().isoformat(),
            tool_name=tool_name,
            tool_input=tool_input,
        )
        self.tool_call_records.append(record)
        logger.info("Tool call recorded: %s", tool_name)
        return record

    def mark_agent_done(self, agent_type: str) -> None:
        """Mark an agent domain as completed (e.g. 'weather', 'transport')."""
        self.agents_completed.add(agent_type)
        logger.info("Agent completed: %s", agent_type)

    def set_last_result(self, result_json: str) -> None:
        """Attach the result JSON to the most recent tool call record."""
        if self.tool_call_records:
            self.tool_call_records[-1].result_json = result_json

    def record_error(self, error_msg: str) -> None:
        """Record an error."""
        self.errors.append(error_msg)
        logger.warning("Error recorded: %s", error_msg)

    def get_summary(self) -> dict:
        """Return a summary of all tracked activity."""
        return {
            "agents_completed": sorted(self.agents_completed),
            "total_tool_calls": len(self.tool_call_records),
            "tools_called": [r.tool_name for r in self.tool_call_records],
            "errors": self.errors,
        }

"""Budget MCP tools — exposed to the budget sub-agent via create_sdk_mcp_server."""

import json
from typing import Any

from claude_agent_sdk import tool

from agents.budget_agent import optimize_budget


@tool(
    "optimize_budget",
    "Aggregate costs, compare against total budget, classify as over/under/balanced, "
    "and generate actionable suggestions. travel_style controls budget utilisation: "
    "'affordable' targets 80% of budget, 'standard' uses 100%, 'premium' stretches "
    "to 120%, 'luxury' has no ceiling.",
    {
        "transport_cost": float,
        "hotel_cost": float,
        "destination": str,
        "num_days": int,
        "total_budget": float,
        "travel_style": str,
    },
)
async def optimize_budget_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Call the budget agent's optimize_budget function."""
    result = await optimize_budget(
        transport_cost=args["transport_cost"],
        hotel_cost=args["hotel_cost"],
        destination=args["destination"],
        num_days=args["num_days"],
        total_budget=args["total_budget"],
        travel_style=args.get("travel_style", "standard"),
    )
    return {
        "content": [
            {"type": "text", "text": result.model_dump_json(indent=2)}
        ]
    }

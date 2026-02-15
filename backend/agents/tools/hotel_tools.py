"""Hotel MCP tools — exposed to the hotel sub-agent via create_sdk_mcp_server."""

import json
from datetime import date
from typing import Any

from claude_agent_sdk import tool

from agents.hotel_agent import search_hotels


@tool(
    "search_hotels",
    "Search for hotels at a destination using SerpAPI Google Hotels. "
    "Returns the top 5 ranked by value score (rating / normalised price).",
    {
        "type": "object",
        "properties": {
            "destination": {"type": "string", "description": "City name."},
            "check_in": {"type": "string", "description": "Check-in date YYYY-MM-DD."},
            "check_out": {"type": "string", "description": "Check-out date YYYY-MM-DD."},
            "budget_per_night": {
                "type": "number",
                "description": "Max USD per night (0 = no limit).",
            },
        },
        "required": ["destination", "check_in", "check_out"],
    },
)
async def search_hotels_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Call the hotel agent's search_hotels function."""
    result = await search_hotels(
        destination=args["destination"],
        check_in=date.fromisoformat(args["check_in"]),
        check_out=date.fromisoformat(args["check_out"]),
        budget_per_night=args.get("budget_per_night", 0.0),
    )
    return {
        "content": [
            {"type": "text", "text": result.model_dump_json(indent=2)}
        ]
    }

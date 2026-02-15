"""Transport MCP tools — exposed to the transport sub-agent via create_sdk_mcp_server."""

import json
from datetime import date
from typing import Any

from claude_agent_sdk import tool

from agents.transport_agent import search_flights


@tool(
    "search_flights",
    "Search for flights between origin and destination using SerpAPI Google Flights. "
    "Returns the top 3 options tagged as cheapest, fastest, and best_value.",
    {
        "origin": str,
        "destination": str,
        "start_date": str,
        "end_date": str,
    },
)
async def search_flights_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Call the transport agent's search_flights function."""
    result = await search_flights(
        origin=args["origin"],
        destination=args["destination"],
        start_date=date.fromisoformat(args["start_date"]),
        end_date=date.fromisoformat(args["end_date"]),
    )
    return {
        "content": [
            {"type": "text", "text": result.model_dump_json(indent=2)}
        ]
    }

"""Discovery MCP tools — exposed to the discovery sub-agent via create_sdk_mcp_server."""

import json
from typing import Any

from claude_agent_sdk import tool

from agents.discovery_agent import run_discovery


@tool(
    "discover_places",
    "Find top attractions, restaurants, and hidden gems for a destination using SerpAPI. "
    "Filters by rating, weather viability, and user preferences/dislikes. "
    "Use cuisine_preferences to filter restaurants by cuisine type (e.g. ['indian', 'japanese']).",
    {
        "type": "object",
        "properties": {
            "destination": {"type": "string", "description": "City name."},
            "outdoor_viable": {
                "type": "boolean",
                "description": "Whether outdoor activities are viable given weather.",
            },
            "preferences": {
                "type": "array",
                "items": {"type": "string"},
                "description": "User preferences, e.g. ['museums', 'food'].",
            },
            "dislikes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Things user dislikes, e.g. ['crowds'].",
            },
            "cuisine_preferences": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific cuisine types for restaurants, e.g. ['indian', 'japanese', 'italian']. When provided, only restaurants matching these cuisines will be returned.",
            },
        },
        "required": ["destination"],
    },
)
async def discover_places_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Call the discovery agent's run_discovery function."""
    result = await run_discovery(
        destination=args["destination"],
        outdoor_viable=args.get("outdoor_viable", True),
        preferences=args.get("preferences"),
        dislikes=args.get("dislikes"),
        cuisine_preferences=args.get("cuisine_preferences"),
    )
    return {
        "content": [
            {"type": "text", "text": result.model_dump_json(indent=2)}
        ]
    }

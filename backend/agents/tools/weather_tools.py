"""Weather MCP tools — exposed to the weather sub-agent via create_sdk_mcp_server."""

import json
from datetime import date
from typing import Any

from claude_agent_sdk import tool

from agents.weather_agent import fetch_weather


@tool(
    "get_weather_forecast",
    "Fetch a multi-day weather forecast for a destination from OpenWeatherMap. "
    "Returns daily temperature, conditions, rain probability, and an outdoor-viability flag.",
    {
        "destination": str,
        "start_date": str,
        "end_date": str,
    },
)
async def get_weather_forecast_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Call the weather agent's fetch_weather function and return the result."""
    result = await fetch_weather(
        destination=args["destination"],
        start_date=date.fromisoformat(args["start_date"]),
        end_date=date.fromisoformat(args["end_date"]),
    )
    return {
        "content": [
            {"type": "text", "text": result.model_dump_json(indent=2)}
        ]
    }

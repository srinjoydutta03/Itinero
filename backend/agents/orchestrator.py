"""
Orchestrator — multi-agent architecture using the Claude Agent SDK.

Architecture
────────────
• 5 **sub-agents** defined via AgentDefinition, each with its own MCP server
  providing domain-specific tools (weather API, flights, hotels, discovery, budget).

• 1 **orchestrator** (ClaudeSDKClient) whose only tool is the built-in `Task`
  tool — it delegates work to sub-agents by name.  The SDK handles spawning,
  tool routing, and result collection automatically.

• Hooks (PreToolUse / PostToolUse) feed every tool call into AgentTracker so
  the web API can extract structured data and render progress events.

This replaces the raw anthropic.Anthropic() message-loop approach with the
official SDK client model, giving us: session continuity for chat, automatic
sub-agent lifecycle, and native MCP tool integration.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from datetime import date
from typing import Any, Optional

from claude_agent_sdk import (
    AgentDefinition,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    AssistantMessage,
    TextBlock,
    ResultMessage,
    create_sdk_mcp_server,
)

from agents.agent_tracker import AgentTracker
from agents.tools.weather_tools import get_weather_forecast_tool
from agents.tools.transport_tools import search_flights_tool
from agents.tools.hotel_tools import search_hotels_tool
from agents.tools.discovery_tools import discover_places_tool
from agents.tools.budget_tools import optimize_budget_tool
from models.model import (
    BudgetOutput,
    CostBreakdown,
    DateRange,
    DiscoveryOutput,
    FlightOption,
    HotelOption,
    HotelOutput,
    PlanRequest,
    SessionState,
    TransportOutput,
    TravelPlanResponse,
    WeatherOutput,
)
from utils.dependency_map import get_affected_agents
from utils.prompt_loader import load_prompt
from utils.session_store import get_session, save_session

logger = logging.getLogger("itinero.agents.orchestrator")

# ── Model configuration ─────────────────────────────────────────────────────
ORCHESTRATOR_MODEL = os.environ.get("ORCHESTRATOR_MODEL", "sonnet")
SUBAGENT_MODEL = os.environ.get("SUBAGENT_MODEL", "haiku")

# ── Load prompts ─────────────────────────────────────────────────────────────
ORCHESTRATOR_PROMPT = load_prompt("orchestrator")
WEATHER_PROMPT = load_prompt("weather")
TRANSPORT_PROMPT = load_prompt("transport")
HOTEL_PROMPT = load_prompt("hotel")
DISCOVERY_PROMPT = load_prompt("discovery")
BUDGET_PROMPT = load_prompt("budget")


# ═════════════════════════════════════════════════════════════════════════════
#  MCP Servers — one per sub-agent domain
# ═════════════════════════════════════════════════════════════════════════════

weather_server = create_sdk_mcp_server(
    name="weather",
    version="1.0.0",
    tools=[get_weather_forecast_tool],
)

transport_server = create_sdk_mcp_server(
    name="transport",
    version="1.0.0",
    tools=[search_flights_tool],
)

hotel_server = create_sdk_mcp_server(
    name="hotel",
    version="1.0.0",
    tools=[search_hotels_tool],
)

discovery_server = create_sdk_mcp_server(
    name="discovery",
    version="1.0.0",
    tools=[discover_places_tool],
)

budget_server = create_sdk_mcp_server(
    name="budget",
    version="1.0.0",
    tools=[optimize_budget_tool],
)


# ═════════════════════════════════════════════════════════════════════════════
#  Agent Definitions — each sub-agent is an independent AI with its own tools
# ═════════════════════════════════════════════════════════════════════════════

def _build_agent_definitions() -> dict[str, AgentDefinition]:
    """Build the AgentDefinition dict for the orchestrator."""
    return {
        "weather-agent": AgentDefinition(
            description=(
                "Use this agent to fetch real-time weather forecasts for any "
                "destination. It calls the OpenWeatherMap API and returns daily "
                "forecasts with temperature, conditions, rain probability, and "
                "outdoor viability assessment. Requires: destination city, "
                "start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)."
            ),
            tools=["mcp__weather__get_weather_forecast"],
            prompt=WEATHER_PROMPT,
            model=SUBAGENT_MODEL,
        ),
        "transport-agent": AgentDefinition(
            description=(
                "Use this agent to search for flights between an origin and "
                "destination. It calls the SerpAPI Google Flights engine and "
                "returns the top 3 options tagged as cheapest, fastest, and "
                "best_value with prices and durations. Requires: origin, "
                "destination, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)."
            ),
            tools=["mcp__transport__search_flights"],
            prompt=TRANSPORT_PROMPT,
            model=SUBAGENT_MODEL,
        ),
        "hotel-agent": AgentDefinition(
            description=(
                "Use this agent to search for hotels at a destination. It "
                "calls the SerpAPI Google Hotels engine and returns the top 5 "
                "options ranked by value score (rating / price). Requires: "
                "destination, check_in (YYYY-MM-DD), check_out (YYYY-MM-DD), "
                "optional budget_per_night."
            ),
            tools=["mcp__hotel__search_hotels"],
            prompt=HOTEL_PROMPT,
            model=SUBAGENT_MODEL,
        ),
        "discovery-agent": AgentDefinition(
            description=(
                "Use this agent to find top attractions, restaurants, and "
                "hidden local gems for a destination. It calls SerpAPI for "
                "Google Maps results and Reddit-sourced hidden gems. Filters "
                "by rating, weather viability, and user preferences. Requires: "
                "destination. Optional: outdoor_viable, preferences, dislikes, "
                "cuisine_preferences (e.g. ['indian', 'japanese'] to filter "
                "restaurants by specific cuisine types)."
            ),
            tools=["mcp__discovery__discover_places"],
            prompt=DISCOVERY_PROMPT,
            model=SUBAGENT_MODEL,
        ),
        "budget-agent": AgentDefinition(
            description=(
                "Use this agent AFTER transport and hotel agents have returned "
                "their results. It aggregates all cost components (transport, "
                "hotel, food estimates, activities), compares against the "
                "user's total budget using the travel_style multiplier, "
                "classifies as over/under/balanced, and generates actionable "
                "suggestions. Requires: transport_cost, hotel_cost, "
                "destination, num_days, total_budget, travel_style."
            ),
            tools=["mcp__budget__optimize_budget"],
            prompt=BUDGET_PROMPT,
            model=SUBAGENT_MODEL,
        ),
    }


# ═════════════════════════════════════════════════════════════════════════════
#  Hook Factories — wire tool calls into AgentTracker
# ═════════════════════════════════════════════════════════════════════════════

# Map MCP tool names back to agent domain for tracker
_TOOL_TO_AGENT: dict[str, str] = {
    "mcp__weather__get_weather_forecast": "weather",
    "mcp__transport__search_flights": "transport",
    "mcp__hotel__search_hotels": "hotel",
    "mcp__discovery__discover_places": "discovery",
    "mcp__budget__optimize_budget": "budget",
}


def _extract_result_text(tool_response: Any) -> str | None:
    """Extract the inner JSON text from a tool response in any SDK format.

    The SDK may pass tool_response as:
      1. dict  {"content": [{"type": "text", "text": "..."}]}   (MCP format)
      2. str   '{"daily_forecasts": ...}'                       (raw JSON string)
      3. str   '{"content": [{...}]}'                           (serialised MCP)
      4. list  [{"type": "text", "text": "..."}]                (content array)
      5. other — try str() as last resort
    """
    if tool_response is None:
        return None

    # ── Case 1: dict with content array ──────────────────────────────────
    if isinstance(tool_response, dict):
        content = tool_response.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    return block["text"]
        # Maybe it's the raw data dict itself (no wrapper)
        try:
            return json.dumps(tool_response)
        except (TypeError, ValueError):
            return None

    # ── Case 2 / 3: string ───────────────────────────────────────────────
    if isinstance(tool_response, str):
        # Try to unwrap if it's a serialised MCP response
        try:
            parsed = json.loads(tool_response)
            if isinstance(parsed, dict) and "content" in parsed:
                content = parsed["content"]
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            return block["text"]
            # It's already a raw JSON string — use as-is
            return tool_response
        except json.JSONDecodeError:
            return tool_response  # plain text, store anyway

    # ── Case 4: list (content array without wrapper) ─────────────────────
    if isinstance(tool_response, list):
        for block in tool_response:
            if isinstance(block, dict) and block.get("type") == "text":
                return block["text"]

    # ── Fallback ─────────────────────────────────────────────────────────
    return str(tool_response)


def _build_hooks(tracker: AgentTracker) -> dict:
    """Create PreToolUse / PostToolUse hooks wired to the given tracker.

    SDK hook signature:  async def hook(input_data, tool_use_id, context)
      - input_data: dict with 'tool_name', 'tool_input', and (PostToolUse) 'tool_response'
      - tool_use_id: str | None
      - context: HookContext
    """

    async def pre_tool_use(input_data, tool_use_id, context):
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        logger.info("  ⚙ Tool call: %s  args=%s", tool_name, str(tool_input)[:300])
        tracker.record_tool_call(tool_name, tool_input if isinstance(tool_input, dict) else {})
        return {}  # allow the call

    async def post_tool_use(input_data, tool_use_id, context):
        tool_name = input_data.get("tool_name", "")
        tool_response = input_data.get("tool_response", None)
        agent_domain = _TOOL_TO_AGENT.get(tool_name)

        logger.debug(
            "  PostToolUse: tool=%s  domain=%s  response_type=%s  preview=%s",
            tool_name, agent_domain, type(tool_response).__name__,
            str(tool_response)[:500] if tool_response else "None",
        )

        if agent_domain:
            # Search backwards — parallel tools may interleave callbacks
            matched_record = None
            for rec in reversed(tracker.tool_call_records):
                if rec.tool_name == tool_name and rec.result_json is None:
                    matched_record = rec
                    break

            if matched_record:
                result_text = _extract_result_text(tool_response)
                if result_text:
                    matched_record.result_json = result_text
                    logger.info(
                        "  📦 Captured %s result (%d chars)",
                        agent_domain, len(result_text),
                    )
                else:
                    logger.warning(
                        "  ⚠ Could not extract result for %s (type=%s)",
                        agent_domain, type(tool_response).__name__,
                    )
            else:
                logger.warning(
                    "  ⚠ No matching pre-tool record for %s", tool_name,
                )

            tracker.mark_agent_done(agent_domain)
            logger.info("  ✓ Agent domain completed: %s", agent_domain)
        return {}

    return {
        "PreToolUse": [
            HookMatcher(matcher=None, hooks=[pre_tool_use])
        ],
        "PostToolUse": [
            HookMatcher(matcher=None, hooks=[post_tool_use])
        ],
    }


# ═════════════════════════════════════════════════════════════════════════════
#  Build SDK Options
# ═════════════════════════════════════════════════════════════════════════════

def _build_options(tracker: AgentTracker) -> ClaudeAgentOptions:
    """Build ClaudeAgentOptions for the orchestrator client."""
    return ClaudeAgentOptions(
        system_prompt=ORCHESTRATOR_PROMPT,
        permission_mode="bypassPermissions",
        allowed_tools=["Task"],
        agents=_build_agent_definitions(),
        hooks=_build_hooks(tracker),
        model=ORCHESTRATOR_MODEL,
        mcp_servers={
            "weather": weather_server,
            "transport": transport_server,
            "hotel": hotel_server,
            "discovery": discovery_server,
            "budget": budget_server,
        },
    )


# ═════════════════════════════════════════════════════════════════════════════
#  Message Processing
# ═════════════════════════════════════════════════════════════════════════════

def _extract_text_from_messages(messages: list) -> tuple[str, list[dict]]:
    """
    Extract text content and events from SDK messages.

    Returns (final_text, events_list).
    """
    text_parts: list[str] = []
    events: list[dict] = []

    for msg in messages:
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)
                    events.append({"type": "text", "content": block.text})
                elif hasattr(block, "type") and block.type == "tool_use":
                    tool_name = getattr(block, "name", "unknown")
                    tool_input = getattr(block, "input", {})
                    if tool_name == "Task":
                        agent_name = tool_input.get("agent_name", "unknown")
                        events.append({
                            "type": "agent_delegation",
                            "agent_type": agent_name.replace("-agent", ""),
                            "instructions": str(tool_input.get("prompt", ""))[:200],
                        })

    return "\n".join(text_parts), events


# ═════════════════════════════════════════════════════════════════════════════
#  Prompt Builders
# ═════════════════════════════════════════════════════════════════════════════

def _build_plan_prompt(request: PlanRequest) -> str:
    num_days = max((request.end_date - request.start_date).days, 1)
    style = request.travel_style
    style_pct = {"affordable": "80%", "standard": "100%", "premium": "120%", "luxury": "uncapped"}
    budget_per_night = (request.budget_usd * 0.35) / num_days

    return (
        f"Plan a complete trip with the following details:\n\n"
        f"- Destination: {request.destination}\n"
        f"- Origin: {request.origin}\n"
        f"- Dates: {request.start_date.isoformat()} to {request.end_date.isoformat()} "
        f"({num_days} days)\n"
        f"- Total Budget: ${request.budget_usd:.0f} USD\n"
        f"- Travel Style: {style} (target {style_pct.get(style, '100%')} of budget)\n"
        f"- Suggested hotel budget per night: ${budget_per_night:.0f} USD\n"
        f"- Preferences: {', '.join(request.preferences) if request.preferences else 'none'}\n"
        f"- Dislikes: {', '.join(request.dislikes) if request.dislikes else 'none'}\n\n"
        f"Delegate to your sub-agents to gather real data:\n"
        f"1. Delegate to weather-agent, transport-agent, hotel-agent, and "
        f"discovery-agent (can run in parallel)\n"
        f"2. After those complete, delegate to the budget-agent with cost data "
        f"(pass total_budget=${request.budget_usd:.0f} and travel_style=\"{style}\")\n"
        f"3. Provide a comprehensive travel summary with recommendations\n"
    )


def _build_replan_prompt(
    request: PlanRequest,
    changed_fields: list[str],
    affected_agents: set[str],
) -> str:
    num_days = max((request.end_date - request.start_date).days, 1)
    style = request.travel_style
    budget_per_night = (request.budget_usd * 0.35) / num_days

    agent_names = [f"{a}-agent" for a in affected_agents]

    return (
        f"The user has updated their travel plan. Re-run only the affected agents.\n\n"
        f"## Updated Trip Details\n"
        f"- Destination: {request.destination}\n"
        f"- Origin: {request.origin}\n"
        f"- Dates: {request.start_date.isoformat()} to {request.end_date.isoformat()} "
        f"({num_days} days)\n"
        f"- Total Budget: ${request.budget_usd:.0f} USD\n"
        f"- Travel Style: {style}\n"
        f"- Suggested hotel budget per night: ${budget_per_night:.0f} USD\n"
        f"- Preferences: {', '.join(request.preferences) if request.preferences else 'none'}\n"
        f"- Dislikes: {', '.join(request.dislikes) if request.dislikes else 'none'}\n\n"
        f"## What Changed\n"
        f"Changed fields: {', '.join(changed_fields)}\n"
        f"Agents to re-run: {', '.join(agent_names)}\n\n"
        f"Only delegate to the agents listed above, then provide an updated summary."
    )


# ═════════════════════════════════════════════════════════════════════════════
#  Defaults
# ═════════════════════════════════════════════════════════════════════════════

def _default_weather() -> WeatherOutput:
    return WeatherOutput(daily_forecasts=[], outdoor_viable=True, summary="Pending")


def _default_transport() -> TransportOutput:
    return TransportOutput(
        options=[],
        recommended=FlightOption(
            price_usd=0, airlines=[], total_duration_minutes=0, stops=0
        ),
        estimated_cost_usd=0,
    )


def _default_hotel() -> HotelOutput:
    return HotelOutput(
        options=[],
        recommended=HotelOption(name="Pending", total_rate_usd=0),
        estimated_total_usd=0,
    )


def _default_discovery() -> DiscoveryOutput:
    return DiscoveryOutput(attractions=[], hidden_gems=[], restaurants=[])


def _default_budget(total: float) -> BudgetOutput:
    return BudgetOutput(
        breakdown=CostBreakdown(
            transport_usd=0, hotel_usd=0, food_usd=0, activities_usd=0
        ),
        estimated_total_usd=0,
        total_budget_usd=total,
        remaining_budget_usd=total,
        status="balanced",
        suggestions=[],
    )


# ═════════════════════════════════════════════════════════════════════════════
#  Structured Data Extraction
# ═════════════════════════════════════════════════════════════════════════════

def _extract_structured_data(
    tracker: AgentTracker,
    budget_usd: float,
) -> dict:
    """Extract Pydantic models from the tracker's tool-call results."""
    data: dict[str, Any] = {}

    logger.info(
        "Extracting structured data from %d tool records",
        len(tracker.tool_call_records),
    )

    for record in tracker.tool_call_records:
        logger.debug(
            "  Record: tool=%s  has_result=%s  preview=%s",
            record.tool_name,
            record.result_json is not None,
            (record.result_json or "")[:200],
        )
        if record.result_json:
            try:
                parsed = json.loads(record.result_json)
            except json.JSONDecodeError as exc:
                logger.warning(
                    "  ⚠ JSON decode failed for %s: %s", record.tool_name, exc,
                )
                continue

            tool_name = record.tool_name
            try:
                if "get_weather_forecast" in tool_name:
                    data["weather"] = WeatherOutput(**parsed)
                    logger.info("  ✓ Parsed weather data")
                elif "search_flights" in tool_name:
                    data["transport"] = TransportOutput(**parsed)
                    logger.info("  ✓ Parsed transport data")
                elif "search_hotels" in tool_name:
                    data["hotel"] = HotelOutput(**parsed)
                    logger.info("  ✓ Parsed hotel data")
                elif "discover_places" in tool_name:
                    data["discovery"] = DiscoveryOutput(**parsed)
                    logger.info("  ✓ Parsed discovery data")
                elif "optimize_budget" in tool_name:
                    data["budget"] = BudgetOutput(**parsed)
                    logger.info("  ✓ Parsed budget data")
            except Exception as exc:
                logger.warning(
                    "  ⚠ Pydantic validation failed for %s: %s", tool_name, exc,
                )

    return data


# ═════════════════════════════════════════════════════════════════════════════
#  Public API — called by routes
# ═════════════════════════════════════════════════════════════════════════════

async def run_full_plan(request: PlanRequest) -> TravelPlanResponse:
    """Run the full multi-agent travel planning pipeline."""
    session_id = str(uuid.uuid4())
    tracker = AgentTracker()

    logger.info(
        "Starting full plan — session=%s, destination=%s",
        session_id, request.destination,
    )

    prompt = _build_plan_prompt(request)
    options = _build_options(tracker)

    all_messages: list = []

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for msg in client.receive_response():
            all_messages.append(msg)

    final_text, events = _extract_text_from_messages(all_messages)
    structured = _extract_structured_data(tracker, request.budget_usd)
    agents_run = list(tracker.agents_completed)
    num_days = max((request.end_date - request.start_date).days, 1)

    session = SessionState(
        session_id=session_id,
        request=request,
        weather=structured.get("weather"),
        transport=structured.get("transport"),
        hotel=structured.get("hotel"),
        discovery=structured.get("discovery"),
        budget=structured.get("budget"),
        agents_run=agents_run,
        errors=tracker.errors,
    )
    save_session(session)

    response = TravelPlanResponse(
        session_id=session_id,
        destination=request.destination,
        dates=DateRange(
            start_date=request.start_date,
            end_date=request.end_date,
            num_days=num_days,
        ),
        weather=structured.get("weather") or _default_weather(),
        transport=structured.get("transport") or _default_transport(),
        hotel=structured.get("hotel") or _default_hotel(),
        discovery=structured.get("discovery") or _default_discovery(),
        budget=structured.get("budget") or _default_budget(request.budget_usd),
        itinerary=session.itinerary or [],
        agents_run=agents_run,
        replanned_agents=[],
        errors=tracker.errors,
        llm_summary=final_text,
    )

    # Pre-flight check: make sure response serialises cleanly (avoids 422)
    try:
        response.model_dump_json()
    except Exception as ser_exc:
        logger.error("Response serialisation pre-flight FAILED: %s", ser_exc)
        for field_name in ["weather", "transport", "hotel", "discovery", "budget", "dates"]:
            val = getattr(response, field_name, None)
            if val is not None:
                try:
                    val.model_dump_json()
                except Exception as f_exc:
                    logger.error("  Field '%s' fails: %s", field_name, f_exc)

    logger.info(
        "Plan complete — session=%s, agents_run=%s, tool_calls=%d",
        session_id, agents_run, len(tracker.tool_call_records),
    )
    return response


async def run_replan(
    session_id: str,
    updated_preferences: dict,
) -> TravelPlanResponse:
    """Selectively re-plan parts of an existing travel plan."""
    session = get_session(session_id)
    if session is None:
        raise ValueError(f"Session not found: {session_id}")

    changed_fields = list(updated_preferences.keys())
    affected = get_affected_agents(changed_fields)

    if not affected:
        logger.info("No agents affected by changes: %s", changed_fields)
        return _session_to_response(session, replanned=[])

    request_data = session.request.model_dump()
    request_data.update(updated_preferences)
    updated_request = PlanRequest(**request_data)

    tracker = AgentTracker()
    prompt = _build_replan_prompt(updated_request, changed_fields, affected)
    options = _build_options(tracker)

    all_messages: list = []

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for msg in client.receive_response():
            all_messages.append(msg)

    final_text, events = _extract_text_from_messages(all_messages)
    structured = _extract_structured_data(tracker, updated_request.budget_usd)
    replanned = list(tracker.agents_completed)

    if "weather" in structured:
        session.weather = structured["weather"]
    if "transport" in structured:
        session.transport = structured["transport"]
    if "hotel" in structured:
        session.hotel = structured["hotel"]
    if "discovery" in structured:
        session.discovery = structured["discovery"]
    if "budget" in structured:
        session.budget = structured["budget"]

    session.request = updated_request
    session.replanned_agents = replanned
    session.errors.extend(tracker.errors)
    save_session(session)

    response = _session_to_response(session, replanned=replanned)
    response.llm_summary = final_text
    return response


def _session_to_response(
    session: SessionState,
    replanned: list[str],
) -> TravelPlanResponse:
    num_days = max(
        (session.request.end_date - session.request.start_date).days, 1
    )
    return TravelPlanResponse(
        session_id=session.session_id,
        destination=session.request.destination,
        dates=DateRange(
            start_date=session.request.start_date,
            end_date=session.request.end_date,
            num_days=num_days,
        ),
        weather=session.weather or _default_weather(),
        transport=session.transport or _default_transport(),
        hotel=session.hotel or _default_hotel(),
        discovery=session.discovery or _default_discovery(),
        budget=session.budget or _default_budget(session.request.budget_usd),
        itinerary=session.itinerary or [],
        agents_run=session.agents_run,
        replanned_agents=replanned,
        errors=session.errors,
    )


# ═════════════════════════════════════════════════════════════════════════════
#  Chat API — multi-turn conversations via persistent ClaudeSDKClient
# ═════════════════════════════════════════════════════════════════════════════

# Active chat clients — keyed by session_id
_chat_clients: dict[str, ClaudeSDKClient] = {}


def _build_plan_context(session: SessionState) -> str:
    """Build a context summary of the existing plan for the chat client."""
    req = session.request
    lines = [
        f"The user already has a completed travel plan. Here is the context:",
        f"- Destination: {req.destination}",
        f"- Origin: {req.origin}",
        f"- Dates: {req.start_date} to {req.end_date}",
        f"- Budget: ${req.budget_usd}",
        f"- Travel Style: {req.travel_style}",
        f"- Travelers: {getattr(req, 'travelers', 2)}",
    ]
    if req.preferences:
        lines.append(f"- Preferences: {', '.join(req.preferences)}")
    if req.dislikes:
        lines.append(f"- Dislikes: {', '.join(req.dislikes)}")

    if session.weather:
        lines.append(f"\nWeather: {session.weather.summary}")
    if session.transport:
        rec = session.transport.recommended
        lines.append(
            f"\nTransport: Recommended flight — {', '.join(rec.airlines)}, "
            f"${rec.price_usd}, {rec.stops} stop(s), "
            f"est. round-trip ${session.transport.estimated_cost_usd}"
        )
        lines.append(f"  Other options: {len(session.transport.options)} flights found")
    if session.hotel:
        rec = session.hotel.recommended
        lines.append(
            f"\nHotel: Recommended — {rec.name}, "
            f"${rec.rate_per_night_usd}/night, rating {rec.rating}, "
            f"total ${rec.total_rate_usd}"
        )
        lines.append(f"  Other options: {len(session.hotel.options)} hotels found")
    if session.discovery:
        lines.append(
            f"\nDiscovery: {len(session.discovery.attractions)} attractions, "
            f"{len(session.discovery.hidden_gems)} hidden gems, "
            f"{len(session.discovery.restaurants)} restaurants"
        )
        if session.discovery.attractions:
            att_names = [a.name for a in session.discovery.attractions[:8]]
            lines.append(f"  Attractions: {', '.join(att_names)}")
        if session.discovery.restaurants:
            rest_names = [r.name for r in session.discovery.restaurants[:6]]
            lines.append(f"  Restaurants: {', '.join(rest_names)}")
        if session.discovery.hidden_gems:
            gem_names = [g.name for g in session.discovery.hidden_gems[:5]]
            lines.append(f"  Hidden Gems: {', '.join(gem_names)}")
    if session.budget:
        b = session.budget
        lines.append(
            f"\nBudget: Total est. ${b.estimated_total_usd}, "
            f"remaining ${b.remaining_budget_usd}"
        )
        lines.append(
            f"  Breakdown: transport ${b.breakdown.transport_usd}, "
            f"hotel ${b.breakdown.hotel_usd}, "
            f"food ${b.breakdown.food_usd}, "
            f"activities ${b.breakdown.activities_usd}"
        )

    lines.append(
        "\nThe user is now chatting to modify or ask questions about this plan. "
        "You already have full context — do NOT ask them to repeat their destination, "
        "dates, budget, or other details. Use the sub-agents via the Task tool if "
        "you need to search for updated flights, hotels, etc."
    )
    return "\n".join(lines)


async def run_chat_turn(
    session_id: str | None,
    user_message: str,
    tracker: AgentTracker,
) -> dict:
    """
    Run a single chat turn using a persistent ClaudeSDKClient.

    The SDK client maintains full conversation context across turns
    automatically — no manual message history management needed.

    On the first turn, if we have an existing plan for this session,
    we inject the plan context so the LLM knows the current state.
    """
    is_new_client = False

    # Reset tracker so stale records from prior turns don't leak
    tracker.reset()

    if session_id and session_id in _chat_clients:
        client = _chat_clients[session_id]
    else:
        session_id = session_id or str(uuid.uuid4())
        options = _build_options(tracker)
        client = ClaudeSDKClient(options=options)
        await client.connect()
        _chat_clients[session_id] = client
        is_new_client = True

    # On first chat turn, inject existing plan context so the LLM
    # doesn't ask the user to repeat their trip details.
    if is_new_client:
        session = get_session(session_id)
        if session:
            context = _build_plan_context(session)
            logger.info(
                "Injecting plan context into chat session %s (%d chars)",
                session_id, len(context),
            )
            await client.query(context)
            # Consume the context response silently
            async for _ in client.receive_response():
                pass

    await client.query(user_message)

    all_messages: list = []
    async for msg in client.receive_response():
        all_messages.append(msg)

    final_text, events = _extract_text_from_messages(all_messages)

    # Check if any agents were triggered during this chat turn.
    # If so, extract the structured data and update the session.
    updated_plan_dict = None
    if tracker.tool_call_records:
        session = get_session(session_id)
        if session:
            structured = _extract_structured_data(tracker, session.request.budget_usd)
            if structured:
                logger.info(
                    "Chat turn triggered agent updates: %s",
                    list(structured.keys()),
                )
                if "weather" in structured:
                    session.weather = structured["weather"]
                if "transport" in structured:
                    session.transport = structured["transport"]
                if "hotel" in structured:
                    session.hotel = structured["hotel"]
                if "discovery" in structured:
                    session.discovery = structured["discovery"]
                if "budget" in structured:
                    session.budget = structured["budget"]
                save_session(session)

                # Build the full response so the frontend can update
                response_obj = _session_to_response(
                    session, replanned=list(structured.keys()),
                )
                response_obj.llm_summary = final_text
                updated_plan_dict = response_obj.model_dump(mode="json")

    return {
        "text": final_text,
        "events": events,
        "summary": tracker.get_summary(),
        "session_id": session_id,
        "updated_plan": updated_plan_dict,
    }


async def close_chat_session(session_id: str) -> None:
    """Disconnect and remove a chat session's SDK client."""
    client = _chat_clients.pop(session_id, None)
    if client:
        try:
            await client.disconnect()
        except Exception:
            pass
    logger.info("Chat session closed: %s", session_id)

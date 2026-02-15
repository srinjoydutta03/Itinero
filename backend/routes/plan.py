"""POST /api/plan — Create a new travel plan."""

import logging

from fastapi import APIRouter, HTTPException

from models.model import PlanRequest, TravelPlanResponse
from agents.orchestrator import run_full_plan

logger = logging.getLogger("itinero.routes.plan")

router = APIRouter()


@router.post("/api/plan", response_model=TravelPlanResponse)
async def create_plan(request: PlanRequest) -> TravelPlanResponse:
    """
    Generate a complete travel plan.

    Runs the full orchestration pipeline:
    1. Weather, Transport, Hotel, Discovery agents in parallel
    2. Budget agent (sequential, needs Phase 1 costs)
    3. Itinerary builder

    Returns the complete travel plan response with session ID for re-planning.
    """
    logger.info(
        "POST /api/plan — destination=%s, dates=%s to %s, budget=$%.0f, origin=%s",
        request.destination,
        request.start_date,
        request.end_date,
        request.budget_usd,
        request.origin,
    )
    logger.info(
        "  preferences=%s, dislikes=%s",
        request.preferences,
        request.dislikes,
    )

    try:
        response = await run_full_plan(request)
        logger.info(
            "Plan created — session=%s, agents_run=%s, errors=%d",
            response.session_id,
            response.agents_run,
            len(response.errors),
        )
        return response
    except Exception as exc:
        logger.exception("Unhandled error in /api/plan")
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {exc}")

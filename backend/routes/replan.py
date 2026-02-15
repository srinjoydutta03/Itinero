"""POST /api/replan — Selectively update an existing travel plan."""

import logging

from fastapi import APIRouter, HTTPException

from models.model import ReplanRequest, TravelPlanResponse
from agents.orchestrator import run_replan

logger = logging.getLogger("itinero.routes.replan")

router = APIRouter()


@router.post("/api/replan", response_model=TravelPlanResponse)
async def replan(request: ReplanRequest) -> TravelPlanResponse:
    """
    Selectively re-plan parts of an existing travel plan.

    Accepts a session_id and a dict of updated preferences. Only the agents
    affected by the changed fields are re-run; everything else is preserved.
    """
    logger.info(
        "POST /api/replan — session=%s, updated_fields=%s",
        request.session_id,
        list(request.updated_preferences.keys()),
    )

    try:
        response = await run_replan(
            session_id=request.session_id,
            updated_preferences=request.updated_preferences,
        )
        logger.info(
            "Replan complete — session=%s, replanned=%s, errors=%d",
            response.session_id,
            response.replanned_agents,
            len(response.errors),
        )
        return response
    except ValueError as exc:
        logger.warning("Replan failed — session not found: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.exception("Unhandled error in /api/replan")
        raise HTTPException(status_code=500, detail=f"Replan failed: {exc}")

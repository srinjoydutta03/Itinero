"""GET /api/session/{session_id} — Retrieve a stored session."""

import logging

from fastapi import APIRouter, HTTPException

from models.model import SessionState
from utils.session_store import get_session

logger = logging.getLogger("itinero.routes.session")

router = APIRouter()


@router.get("/api/session/{session_id}", response_model=SessionState)
async def get_session_endpoint(session_id: str) -> SessionState:
    """
    Retrieve the full session state including raw agent outputs and final itinerary.
    """
    logger.info("GET /api/session/%s", session_id)

    session = get_session(session_id)
    if session is None:
        logger.warning("Session not found: %s", session_id)
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    return session

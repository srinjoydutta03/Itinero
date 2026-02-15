"""In-memory session store for travel planning sessions."""

import logging
from datetime import datetime
from typing import Optional

from models.model import SessionState

logger = logging.getLogger("itinero.session_store")

# ─── In-memory singleton store ───────────────────────────────────────────────
sessions: dict[str, SessionState] = {}


def save_session(session: SessionState) -> None:
    """Save or update a session in the store."""
    session.updated_at = datetime.utcnow()
    sessions[session.session_id] = session
    logger.info("Session saved: %s", session.session_id)


def get_session(session_id: str) -> Optional[SessionState]:
    """Retrieve a session by its ID."""
    session = sessions.get(session_id)
    if session is None:
        logger.warning("Session not found: %s", session_id)
    return session


def delete_session(session_id: str) -> bool:
    """Delete a session. Returns True if it existed."""
    if session_id in sessions:
        del sessions[session_id]
        logger.info("Session deleted: %s", session_id)
        return True
    return False


def list_sessions() -> list[str]:
    """Return all session IDs."""
    return list(sessions.keys())

"""
Client manager — session manager for chat conversations.

With the Claude Agent SDK, each chat session has a persistent ClaudeSDKClient
managed by the orchestrator module. This module provides a simple manager for
session lifecycle (creation, expiry, cleanup) and per-session AgentTrackers.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

from agents.agent_tracker import AgentTracker

logger = logging.getLogger("itinero.utils.client_manager")

# Session TTL — how long an idle chat session stays alive
SESSION_TTL_MINUTES = int(os.environ.get("CHAT_SESSION_TTL_MINUTES", "30"))


@dataclass
class ChatSession:
    """Holds metadata and a tracker for a chat session."""
    session_id: str
    tracker: AgentTracker
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        """Update last_active timestamp."""
        self.last_active = datetime.utcnow()

    @property
    def is_expired(self) -> bool:
        """Check if the session has been idle too long."""
        return datetime.utcnow() - self.last_active > timedelta(
            minutes=SESSION_TTL_MINUTES
        )


class ClientManager:
    """
    Manages chat session metadata and trackers.

    No longer manages SDK clients — the Anthropic API is stateless and
    conversation history is stored in the orchestrator module.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ChatSession] = {}
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("ClientManager started — TTL=%dm", SESSION_TTL_MINUTES)

    async def stop(self) -> None:
        """Stop the cleanup task and close all sessions."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None

        for sid in list(self._sessions):
            await self.close_session(sid)

        logger.info("ClientManager stopped — all sessions closed")

    async def get_or_create(
        self,
        session_id: Optional[str] = None,
    ) -> ChatSession:
        """
        Get an existing chat session or create a new one.

        Args:
            session_id: Existing session ID, or None to create a new session.

        Returns:
            A ChatSession with a tracker.
        """
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            if not session.is_expired:
                session.touch()
                return session
            else:
                # Expired — remove and recreate
                await self._remove_session(session_id)

        new_id = session_id or str(uuid.uuid4())
        tracker = AgentTracker()

        session = ChatSession(
            session_id=new_id,
            tracker=tracker,
        )
        self._sessions[new_id] = session
        logger.info("Chat session created: %s", new_id)
        return session

    async def close_session(self, session_id: str) -> None:
        """Close and remove a chat session."""
        await self._remove_session(session_id)

    async def _remove_session(self, session_id: str) -> None:
        """Remove a session and clean up its SDK client."""
        session = self._sessions.pop(session_id, None)
        if session:
            # Also clean up the SDK client in the orchestrator
            try:
                from agents.orchestrator import close_chat_session
                await close_chat_session(session_id)
            except Exception:
                pass
            logger.info("Chat session closed: %s", session_id)

    async def _cleanup_loop(self) -> None:
        """Periodically remove expired sessions."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                expired = [
                    sid
                    for sid, s in self._sessions.items()
                    if s.is_expired
                ]
                for sid in expired:
                    logger.info("Cleaning up expired session: %s", sid)
                    await self._remove_session(sid)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Cleanup loop error: %s", exc)


# ── Module-level singleton ───────────────────────────────────────────────────
_manager: Optional[ClientManager] = None


def get_client_manager() -> ClientManager:
    """Get the global ClientManager singleton."""
    global _manager
    if _manager is None:
        _manager = ClientManager()
    return _manager

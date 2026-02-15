"""POST /api/chat — Multi-turn chat interface for travel planning.

The orchestrator uses a persistent ClaudeSDKClient per chat session,
maintaining full conversation context across turns automatically.
The ClientManager tracks session metadata (TTL, cleanup).
"""

import logging

from fastapi import APIRouter, HTTPException

from agents.orchestrator import run_chat_turn
from models.model import ChatRequest, ChatResponse
from utils.client_manager import get_client_manager

logger = logging.getLogger("itinero.routes.chat")

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the travel planning orchestrator.

    - If `session_id` is null/omitted, a new chat session is created.
    - If `session_id` is provided, the existing session is reused
      (multi-turn conversation with full context).

    The orchestrator will use the Task tool to spawn sub-agents
    as needed based on the user's message.
    """
    logger.info(
        "POST /api/chat — session=%s, message=%s",
        request.session_id or "(new)",
        request.message[:100],
    )

    try:
        manager = get_client_manager()
        session = await manager.get_or_create(request.session_id)
        session.touch()

        result = await run_chat_turn(
            session_id=session.session_id,
            user_message=request.message,
            tracker=session.tracker,
        )

        response = ChatResponse(
            session_id=session.session_id,
            reply=result["text"],
            events=result["events"],
            agent_summary=result["summary"],
            updated_plan=result.get("updated_plan"),
        )

        logger.info(
            "Chat response — session=%s, events=%d, reply_len=%d",
            session.session_id,
            len(result["events"]),
            len(result["text"]),
        )

        return response

    except Exception as exc:
        logger.exception("Error in /api/chat")
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {exc}",
        )


@router.delete("/api/chat/{session_id}")
async def end_chat(session_id: str):
    """
    End a chat session and release resources.
    """
    manager = get_client_manager()
    await manager.close_session(session_id)
    return {"status": "ok", "message": f"Session {session_id} closed"}

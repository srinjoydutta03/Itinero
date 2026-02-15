import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# ── Logging setup ────────────────────────────────────────────────────────────
# Use an explicit handler on the "itinero" logger so uvicorn's root-logger
# reconfiguration doesn't silence our output.
_formatter = logging.Formatter(
    "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_console = logging.StreamHandler(sys.stdout)
_console.setFormatter(_formatter)

_app_logger = logging.getLogger("itinero")
_app_logger.setLevel(logging.DEBUG)
_app_logger.addHandler(_console)
_app_logger.propagate = False          # don't let uvicorn's root logger swallow it

logger = _app_logger


def _validate_env_vars() -> None:
    """Check all required environment variables are present at startup."""
    required = {
        "ANTHROPIC_API_KEY": "Anthropic Claude API key (Agent SDK backbone)",
        "SERPAPI_KEY": "SerpAPI key (flights, hotels, maps, search)",
        "OPENWEATHER_KEY": "OpenWeatherMap API key (weather forecasts)",
    }
    missing: list[str] = []
    for var, description in required.items():
        if not os.environ.get(var):
            missing.append(f"  • {var} — {description}")

    if missing:
        msg = (
            "\n╔══════════════════════════════════════════════════════════╗\n"
            "║  MISSING ENVIRONMENT VARIABLES                         ║\n"
            "╚══════════════════════════════════════════════════════════╝\n"
            + "\n".join(missing) + "\n\n"
            "Set them in a .env file in the backend/ directory.\n"
            "See .env.example for the template.\n"
        )
        logger.critical(msg)


# ── Always create the app first so uvicorn can find it ───────────────────────
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Itinero",
    description="Agentic travel orchestration system — multi-agent travel planning API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log full validation error details so 422s are easy to diagnose."""
    body = await request.body()
    logger.error(
        "Validation error on %s %s\n  Body: %s\n  Errors: %s",
        request.method,
        request.url.path,
        body.decode("utf-8", errors="replace")[:500],
        exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# ── Validate env vars (warn but don't crash) ────────────────────────────────
_validate_env_vars()

# ── Import and register routers ─────────────────────────────────────────────
try:
    from routes.plan import router as plan_router
    from routes.replan import router as replan_router
    from routes.session import router as session_router
    from routes.chat import router as chat_router
    from utils.client_manager import get_client_manager

    app.include_router(plan_router, tags=["Plan"])
    app.include_router(replan_router, tags=["Replan"])
    app.include_router(session_router, tags=["Session"])
    app.include_router(chat_router, tags=["Chat"])

    _routers_loaded = True
except Exception as exc:
    logger.exception("Failed to load route modules: %s", exc)
    _routers_loaded = False

@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Itinero",
        "version": "1.0.0",
    }


@app.on_event("startup")
async def startup_event():
    """Start the ClientManager for chat sessions on app startup."""
    if _routers_loaded:
        manager = get_client_manager()
        await manager.start()
        logger.info("ClientManager started")
    else:
        logger.warning("Routers not loaded — skipping ClientManager startup")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the ClientManager and clean up all chat sessions on shutdown."""
    if _routers_loaded:
        manager = get_client_manager()
        await manager.stop()
        logger.info("ClientManager stopped")


@app.get("/api/health", tags=["Health"])
async def api_health():
    """Detailed API health check with env var status."""
    return {
        "status": "ok",
        "service": "Itinero",
        "version": "1.0.0",
        "keys_configured": {
            "ANTHROPIC_API_KEY": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "SERPAPI_KEY": bool(os.environ.get("SERPAPI_KEY")),
            "OPENWEATHER_KEY": bool(os.environ.get("OPENWEATHER_KEY")),
        },
    }


# ─── Entrypoint ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    logger.info("Starting Itinero on port %d", port)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    )
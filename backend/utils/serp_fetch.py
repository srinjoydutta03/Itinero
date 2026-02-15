"""Shared async SerpAPI fetch utility with retry logic."""

import asyncio
import logging
import os

import httpx

logger = logging.getLogger("itinero.serp_fetch")

SERPAPI_BASE_URL = "https://serpapi.com/search.json"


async def serp_fetch(params: dict) -> dict:
    """
    Perform an async SerpAPI request with automatic API key injection and retry logic.

    Args:
        params: Query parameters for the SerpAPI endpoint (engine, q, etc.).

    Returns:
        Parsed JSON response as a dict, or empty dict on final failure.
    """
    api_key = os.environ.get("SERPAPI_KEY", "")
    if not api_key:
        logger.error("SERPAPI_KEY is not set in environment variables.")
        return {}

    params["api_key"] = api_key
    params.setdefault("output", "json")

    max_retries = 2
    delay_seconds = 1.0

    for attempt in range(1, max_retries + 2):  # up to 3 attempts (initial + 2 retries)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(SERPAPI_BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                logger.debug(
                    "SerpAPI request succeeded on attempt %d for engine=%s",
                    attempt,
                    params.get("engine", "unknown"),
                )
                return data
        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as exc:
            logger.warning(
                "SerpAPI request attempt %d/%d failed for engine=%s: %s",
                attempt,
                max_retries + 1,
                params.get("engine", "unknown"),
                str(exc),
            )
            if attempt <= max_retries:
                await asyncio.sleep(delay_seconds)
            else:
                logger.error(
                    "SerpAPI request exhausted all retries for engine=%s, params=%s",
                    params.get("engine", "unknown"),
                    {k: v for k, v in params.items() if k != "api_key"},
                )
                return {}
        except Exception as exc:
            logger.error(
                "Unexpected error during SerpAPI request for engine=%s: %s",
                params.get("engine", "unknown"),
                str(exc),
            )
            return {}

    return {}

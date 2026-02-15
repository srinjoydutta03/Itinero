"""Utility for loading agent system prompts from prompts/ directory.

Looks for prompts in two locations (in order of priority):
1. PROJECT_ROOT/prompts/{agent_name}.txt
2. PROJECT_ROOT/.claude/prompts/{agent_name}.txt (legacy fallback)
"""

from __future__ import annotations
import logging
import sys
from pathlib import Path
from functools import lru_cache

logger = logging.getLogger("itinero.utils.prompt_loader")

# Get the project root directory (parent of utils/)
PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
LEGACY_PROMPTS_DIR = PROJECT_ROOT / ".claude" / "prompts"


@lru_cache(maxsize=32)
def load_prompt(agent_name: str) -> str:
    """
    Load system prompt for the specified agent from ./prompts directory.

    Args:
        agent_name: Name of the agent (e.g., "orchestrator", "weather", "transport")

    Returns:
        The prompt text as a string

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
        RuntimeError: If there's an error reading the file

    Example:
        >>> orchestrator_prompt = load_prompt("orchestrator")
        >>> weather_prompt = load_prompt("weather")
    """
    prompt_file = PROMPTS_DIR / f"{agent_name}.txt"

    # Fallback to legacy .claude/prompts/ if not in primary location
    if not prompt_file.exists():
        prompt_file = LEGACY_PROMPTS_DIR / f"{agent_name}.txt"

    if not prompt_file.exists():
        error_msg = (
            f"Prompt file not found: {prompt_file}\n"
            f"Expected location: .claude/prompts/{agent_name}.txt\n"
            f"Available prompts: {list_available_prompts()}"
        )
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt = f.read().strip()

        if not prompt:
            logger.warning(f"Prompt file {agent_name}.txt is empty")

        logger.debug(f"Loaded prompt for {agent_name} ({len(prompt)} chars)")
        return prompt

    except Exception as exc:
        error_msg = f"Failed to read prompt file {prompt_file}: {exc}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from exc


def list_available_prompts() -> list[str]:
    """
    List all available prompt files across both prompt directories.

    Returns:
        List of agent names (without .txt extension)
    """
    agent_names: set[str] = set()

    for directory in [PROMPTS_DIR, LEGACY_PROMPTS_DIR]:
        if not directory.exists():
            continue
        try:
            prompt_files = list(directory.glob("*.txt"))
            for f in prompt_files:
                agent_names.add(f.stem)
        except Exception as exc:
            logger.error(f"Failed to list prompts in {directory}: {exc}")

    return sorted(agent_names)


def get_prompt_path(agent_name: str) -> Path:
    """
    Get the file path for a specific agent's prompt.

    Args:
        agent_name: Name of the agent

    Returns:
        Path object pointing to the prompt file

    Example:
        >>> path = get_prompt_path("weather")
        >>> print(path)
        PosixPath('/path/to/Itinero/.claude/prompts/weather.txt')
    """
    return PROMPTS_DIR / f"{agent_name}.txt"


def validate_prompts() -> dict[str, bool]:
    """
    Validate that all expected agent prompts exist and are readable.

    Returns:
        Dictionary mapping agent names to validation status (True if valid)

    Example:
        >>> results = validate_prompts()
        >>> print(results)
        {
            'orchestrator': True,
            'weather': True,
            'transport': True,
            'hotel': True,
            'discovery': True,
            'budget': True
        }
    """
    expected_agents = [
        "orchestrator",
        "weather",
        "transport",
        "hotel",
        "discovery",
        "budget",
    ]

    results = {}
    for agent in expected_agents:
        try:
            prompt = load_prompt(agent)
            results[agent] = bool(prompt and len(prompt) > 50)
        except Exception as exc:
            logger.error(f"Validation failed for {agent}: {exc}")
            results[agent] = False

    return results


def reload_prompts() -> None:
    """
    Clear the LRU cache to force reloading of all prompts.

    Useful during development when prompts are being edited.

    Example:
        >>> reload_prompts()  # Clears cache
        >>> prompt = load_prompt("weather")  # Loads fresh from disk
    """
    load_prompt.cache_clear()
    logger.info("Prompt cache cleared - all prompts will be reloaded from disk")


# Startup validation
def _validate_on_import():
    """Run validation when module is imported."""
    found_any = False
    for directory in [PROMPTS_DIR, LEGACY_PROMPTS_DIR]:
        if directory.exists():
            found_any = True
            break
    if not found_any:
        logger.warning(
            f"No prompts directories found.\n"
            f"Checked: {PROMPTS_DIR} and {LEGACY_PROMPTS_DIR}\n"
            "Agents will fail if prompts are not available."
        )
    else:
        available = list_available_prompts()
        logger.info(f"Found {len(available)} agent prompts: {', '.join(available)}")


# Run validation on module import
_validate_on_import()

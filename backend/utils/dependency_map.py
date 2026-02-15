"""Dependency map for selective re-planning."""

# Maps a changed field in PlanRequest to the list of agents/steps that must be re-run.
DEPENDENCY_MAP: dict[str, list[str]] = {
    "preferences":  ["discovery", "itinerary"],
    "dislikes":     ["discovery", "itinerary"],
    "budget_usd":   ["budget", "itinerary"],
    "origin":       ["transport", "budget", "itinerary"],
    "destination":  ["weather", "transport", "hotel", "discovery", "budget", "itinerary"],
    "dates":        ["weather", "transport", "hotel", "budget", "itinerary"],
    "start_date":   ["weather", "transport", "hotel", "budget", "itinerary"],
    "end_date":     ["weather", "transport", "hotel", "budget", "itinerary"],
}


def get_affected_agents(changed_fields: list[str]) -> set[str]:
    """
    Given a list of changed field names, return the union of all agents that
    need to be re-run.

    Args:
        changed_fields: List of field names that were modified (e.g. ["budget_usd", "dislikes"]).

    Returns:
        Set of agent/step names that must be re-executed.
    """
    affected: set[str] = set()
    for field_name in changed_fields:
        deps = DEPENDENCY_MAP.get(field_name, [])
        affected.update(deps)
    return affected

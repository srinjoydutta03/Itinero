"""Discovery agent — attractions, restaurants, and hidden gems via SerpAPI.

Provides the run_discovery function (and helpers search_attractions,
search_restaurants, search_hidden_gems) which are exposed as an MCP tool
(mcp__discovery__discover_places) to the discovery sub-agent via
the Claude Agent SDK.
"""

import logging
import re
from collections import Counter

from models.model import Attraction, DiscoveryOutput, HiddenGem, Restaurant
from utils.serp_fetch import serp_fetch

logger = logging.getLogger("itinero.agents.discovery")

OUTDOOR_TYPES = {"park", "beach", "hiking", "outdoor", "garden", "trail", "waterfall"}

# TODO: Reddit agent will be integrated here


async def search_attractions(
    destination: str,
    outdoor_viable: bool = True,
    dislikes: list[str] | None = None,
) -> list[Attraction]:
    """
    Search for top attractions using SerpAPI Google Maps.

    Filters: rating >= 4.0, removes disliked items, filters outdoor if weather is bad.
    """
    dislikes = dislikes or []

    params = {
        "engine": "google_maps",
        "q": f"top attractions in {destination}",
        "type": "search",
    }

    data = await serp_fetch(params)
    local_results = data.get("local_results", [])

    attractions: list[Attraction] = []
    for item in local_results:
        rating = float(item.get("rating", 0) or 0)
        if rating < 4.0:
            continue

        name = item.get("title", item.get("name", "Unknown"))
        address = item.get("address", "")
        place_type = item.get("type", item.get("types", ""))
        if isinstance(place_type, list):
            place_type = ", ".join(place_type)
        description = item.get("description", item.get("snippet", ""))
        reviews = int(item.get("reviews", 0) or 0)

        # Check if outdoor
        combined_lower = f"{place_type} {name}".lower()
        is_outdoor = any(kw in combined_lower for kw in OUTDOOR_TYPES)

        attractions.append(
            Attraction(
                name=name,
                rating=rating,
                reviews=reviews,
                address=str(address),
                type=str(place_type),
                description=str(description),
                is_outdoor=is_outdoor,
            )
        )

    # Post-processing: remove dislikes
    attractions = _filter_dislikes(attractions, dislikes, key_fn=lambda a: f"{a.name} {a.type}")

    # Filter outdoor if weather is bad
    if not outdoor_viable:
        attractions = [a for a in attractions if not a.is_outdoor]

    return attractions


async def search_restaurants(
    destination: str,
    dietary_preferences: list[str] | None = None,
    dislikes: list[str] | None = None,
    cuisine_preferences: list[str] | None = None,
) -> list[Restaurant]:
    """
    Search for restaurants using SerpAPI Google Maps.

    Filters: rating >= 3.8, removes disliked items.
    When cuisine_preferences are provided, searches specifically for those
    cuisine types and filters results to match.
    """
    dietary_preferences = dietary_preferences or []
    dislikes = dislikes or []
    cuisine_preferences = cuisine_preferences or []

    dietary_str = " ".join(dietary_preferences) if dietary_preferences else ""
    cuisine_str = " ".join(cuisine_preferences) if cuisine_preferences else ""

    # Build search query — cuisine preferences take priority
    if cuisine_str:
        q = f"best {cuisine_str} restaurants in {destination}"
    else:
        q = f"best restaurants in {destination}"
    if dietary_str:
        q += f" {dietary_str}"

    params = {
        "engine": "google_maps",
        "q": q,
        "type": "search",
    }

    data = await serp_fetch(params)
    local_results = data.get("local_results", [])

    restaurants: list[Restaurant] = []
    for item in local_results:
        rating = float(item.get("rating", 0) or 0)
        if rating < 3.8:
            continue

        name = item.get("title", item.get("name", "Unknown"))
        address = item.get("address", "")
        place_type = item.get("type", item.get("types", ""))
        if isinstance(place_type, list):
            place_type = ", ".join(place_type)
        price_level = item.get("price", item.get("price_level", ""))
        if isinstance(price_level, int):
            price_level = "$" * price_level
        reviews = int(item.get("reviews", 0) or 0)

        restaurants.append(
            Restaurant(
                name=name,
                rating=rating,
                address=str(address),
                type=str(place_type),
                price_level=str(price_level),
                reviews=reviews,
            )
        )

    # Post-processing: remove dislikes
    restaurants = _filter_dislikes(restaurants, dislikes, key_fn=lambda r: f"{r.name} {r.type}")

    return restaurants


async def search_hidden_gems(destination: str) -> list[HiddenGem]:
    """
    Search for hidden gems using SerpAPI Google Search (Reddit-sourced).

    Parses organic_results snippets and titles, extracts recurring capitalized
    noun phrase candidates appearing 2+ times.
    """
    params = {
        "engine": "google",
        "q": f"site:reddit.com {destination} hidden gem OR locals only OR underrated",
    }

    data = await serp_fetch(params)
    organic_results = data.get("organic_results", [])

    if not organic_results:
        logger.info("No hidden gems found for %s", destination)
        return []

    # Collect all text from titles and snippets
    all_text_parts: list[str] = []
    snippet_map: dict[str, str] = {}  # name -> snippet for attribution

    for result in organic_results:
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        all_text_parts.append(title)
        all_text_parts.append(snippet)

        # Extract capitalized phrases (potential place names)
        for text in [title, snippet]:
            phrases = _extract_capitalized_phrases(text)
            for phrase in phrases:
                if phrase not in snippet_map:
                    snippet_map[phrase] = snippet

    combined_text = " ".join(all_text_parts)
    phrases = _extract_capitalized_phrases(combined_text)

    # Count occurrences
    phrase_counts = Counter(phrases)

    # Filter: must appear 2+ times, exclude generic words
    generic_words = {
        "Reddit", "Google", "Trip", "Travel", "City", "Place", "Things",
        "Best", "Top", "Guide", "Hotel", "Airport", "The", "You", "Your",
        "What", "Where", "How", "This", "That", "These", "Those",
    }

    gems: list[HiddenGem] = []
    seen_lower: set[str] = set()

    for phrase, count in phrase_counts.most_common(20):
        if count < 2:
            break
        if phrase in generic_words:
            continue
        if len(phrase) < 3:
            continue
        phrase_lower = phrase.lower()
        if phrase_lower in seen_lower:
            continue
        # Exclude the destination name itself
        if phrase_lower in destination.lower():
            continue
        seen_lower.add(phrase_lower)

        gems.append(
            HiddenGem(
                name=phrase,
                source="google/reddit",
                snippet=snippet_map.get(phrase, "")[:200],
                mentions=count,
            )
        )

        if len(gems) >= 10:
            break

    return gems


def _extract_capitalized_phrases(text: str) -> list[str]:
    """Extract capitalized multi-word or single-word proper nouns from text."""
    # Match sequences of capitalized words (2+ word names or single caps words > 3 chars)
    pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"
    matches = re.findall(pattern, text)
    return [m.strip() for m in matches if len(m.strip()) > 2]


def _filter_dislikes(items: list, dislikes: list[str], key_fn) -> list:
    """Remove items whose key contains any dislike word (case-insensitive)."""
    if not dislikes:
        return items
    dislikes_lower = [d.lower() for d in dislikes]
    filtered = []
    for item in items:
        text = key_fn(item).lower()
        if not any(d in text for d in dislikes_lower):
            filtered.append(item)
    return filtered


def _deduplicate_by_name(*lists: list) -> None:
    """
    In-place deduplication across multiple lists by name (case-insensitive).
    Earlier lists take priority — duplicates are removed from later lists.
    """
    seen: set[str] = set()
    for item_list in lists:
        to_remove = []
        for i, item in enumerate(item_list):
            name_lower = item.name.lower()
            if name_lower in seen:
                to_remove.append(i)
            else:
                seen.add(name_lower)
        for idx in reversed(to_remove):
            item_list.pop(idx)


async def run_discovery(
    destination: str,
    outdoor_viable: bool = True,
    preferences: list[str] | None = None,
    dislikes: list[str] | None = None,
    cuisine_preferences: list[str] | None = None,
) -> DiscoveryOutput:
    """
    Run the full discovery pipeline: attractions + restaurants + hidden gems.

    Deduplicates across all three result sets.
    """
    import asyncio

    preferences = preferences or []
    dislikes = dislikes or []
    cuisine_preferences = cuisine_preferences or []

    # Extract dietary preferences from the preferences list
    dietary_keywords = {
        "vegetarian", "vegan", "halal", "kosher", "gluten-free",
        "pescatarian", "keto", "organic", "dairy-free",
    }
    dietary_prefs = [p for p in preferences if p.lower() in dietary_keywords]

    # Also check preferences for cuisine types (non-dietary food preferences)
    # e.g. if user says preferences: ["indian", "museums"], "indian" is a cuisine
    cuisine_keywords = {
        "indian", "chinese", "japanese", "thai", "italian", "french",
        "mexican", "korean", "vietnamese", "greek", "turkish", "spanish",
        "american", "mediterranean", "middle eastern", "ethiopian", "lebanese",
        "peruvian", "brazilian", "german", "british", "african", "caribbean",
        "indonesian", "malaysian", "filipino", "nepalese", "tibetan",
        "sri lankan", "pakistani", "bengali", "sushi", "ramen", "tapas",
        "dim sum", "seafood", "steakhouse", "bbq", "barbecue", "pizza",
    }
    # Merge explicit cuisine_preferences with any cuisine-like preferences
    all_cuisine_prefs = list(cuisine_preferences)
    for p in preferences:
        if p.lower() in cuisine_keywords and p.lower() not in [c.lower() for c in all_cuisine_prefs]:
            all_cuisine_prefs.append(p)

    logger.info(
        "Discovery for %s — cuisine: %s, dietary: %s, dislikes: %s",
        destination, all_cuisine_prefs, dietary_prefs, dislikes,
    )

    # Run all three searches in parallel
    attractions_task = search_attractions(destination, outdoor_viable, dislikes)
    restaurants_task = search_restaurants(destination, dietary_prefs, dislikes, all_cuisine_prefs)
    gems_task = search_hidden_gems(destination)

    attractions, restaurants, hidden_gems = await asyncio.gather(
        attractions_task, restaurants_task, gems_task,
        return_exceptions=False,
    )

    # Handle any exceptions that slipped through
    if isinstance(attractions, BaseException):
        logger.error("Attractions search failed: %s", attractions)
        attractions = []
    if isinstance(restaurants, BaseException):
        logger.error("Restaurants search failed: %s", restaurants)
        restaurants = []
    if isinstance(hidden_gems, BaseException):
        logger.error("Hidden gems search failed: %s", hidden_gems)
        hidden_gems = []

    # Deduplicate across lists
    _deduplicate_by_name(attractions, restaurants)

    return DiscoveryOutput(
        attractions=attractions,
        hidden_gems=hidden_gems,
        restaurants=restaurants,
    )

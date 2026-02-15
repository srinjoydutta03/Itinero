"""Hotel agent — searches hotels via SerpAPI Google Hotels.

Provides the search_hotels function which is exposed as an MCP tool
(mcp__hotel__search_hotels) to the hotel sub-agent via
the Claude Agent SDK.
"""

import logging
from datetime import date

from models.model import HotelOption, HotelOutput
from utils.serp_fetch import serp_fetch

logger = logging.getLogger("itinero.agents.hotel")


async def search_hotels(
    destination: str,
    check_in: date,
    check_out: date,
    budget_per_night: float = 0.0,
) -> HotelOutput:
    """
    Search for hotels using SerpAPI Google Hotels engine.

    Returns the top 5 hotels sorted by value_score (rating / normalized price).
    """
    num_nights = (check_out - check_in).days
    if num_nights <= 0:
        num_nights = 1

    params = {
        "engine": "google_hotels",
        "q": f"hotels in {destination}",
        "check_in_date": check_in.isoformat(),
        "check_out_date": check_out.isoformat(),
        "currency": "USD",
        "adults": 2,
    }

    data = await serp_fetch(params)

    properties = data.get("properties", [])
    if not properties:
        logger.warning("No hotel properties found for %s", destination)
        fallback = HotelOption(
            name="No results found",
            total_rate_usd=0,
            rate_per_night_usd=0,
            rating=0,
        )
        return HotelOutput(options=[], recommended=fallback, estimated_total_usd=0)

    options: list[HotelOption] = []
    for prop in properties:
        name = prop.get("name", "Unknown Hotel")

        # Extract price — SerpAPI returns various formats
        total_rate = 0.0
        rate_info = prop.get("total_rate", prop.get("rate_per_night", {}))
        if isinstance(rate_info, dict):
            extracted = rate_info.get("extracted_lowest", rate_info.get("lowest", 0))
            total_rate = float(extracted) if extracted else 0.0
        elif isinstance(rate_info, (int, float)):
            total_rate = float(rate_info)
        elif isinstance(rate_info, str):
            total_rate = float(rate_info.replace("$", "").replace(",", "").strip() or "0")

        # If we got per-night rate, multiply
        per_night_info = prop.get("rate_per_night", {})
        if isinstance(per_night_info, dict):
            per_night_val = per_night_info.get("extracted_lowest", per_night_info.get("lowest", 0))
            per_night_val = float(per_night_val) if per_night_val else 0.0
        else:
            per_night_val = 0.0

        if total_rate == 0.0 and per_night_val > 0:
            total_rate = per_night_val * num_nights

        rate_per_night = total_rate / num_nights if num_nights > 0 and total_rate > 0 else per_night_val

        rating = float(prop.get("overall_rating", prop.get("rating", 0)) or 0)
        reviews = int(prop.get("reviews", 0) or 0)
        location = prop.get("location", prop.get("neighborhood", ""))
        if isinstance(location, dict):
            location = location.get("name", "")

        amenities_raw = prop.get("amenities", [])
        amenities = amenities_raw if isinstance(amenities_raw, list) else []

        link = prop.get("link", prop.get("serpapi_property_details_link", ""))

        # Compute value score
        value_score = 0.0
        if rate_per_night > 0 and rating > 0:
            value_score = rating / (rate_per_night / 100)  # normalize price to 100s

        if total_rate > 0:
            options.append(
                HotelOption(
                    name=name,
                    total_rate_usd=round(total_rate, 2),
                    rate_per_night_usd=round(rate_per_night, 2),
                    rating=rating,
                    reviews=reviews,
                    location=str(location),
                    amenities=[str(a) for a in amenities[:10]],
                    link=str(link),
                    value_score=round(value_score, 3),
                )
            )

    # Sort by value_score descending, take top 5
    options.sort(key=lambda h: h.value_score, reverse=True)
    top5 = options[:5]

    if not top5:
        fallback = HotelOption(
            name="No valid hotels found",
            total_rate_usd=0,
            rate_per_night_usd=0,
        )
        return HotelOutput(options=[], recommended=fallback, estimated_total_usd=0)

    recommended = top5[0]

    return HotelOutput(
        options=top5,
        recommended=recommended,
        estimated_total_usd=recommended.total_rate_usd,
    )

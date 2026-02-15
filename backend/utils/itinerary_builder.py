"""Itinerary builder — pure function that assembles day-by-day plans."""

from datetime import date, timedelta
from typing import Optional

from models.model import (
    Attraction,
    BudgetOutput,
    DailyForecast,
    DayPlan,
    DiscoveryOutput,
    HiddenGem,
    HotelOutput,
    MealPlan,
    Restaurant,
    WeatherOutput,
)

OUTDOOR_KEYWORDS = {"park", "beach", "hiking", "outdoor", "garden", "trail", "waterfall"}

# Tier-based generic meal suggestions
MEAL_SUGGESTIONS = {
    "budget":   {"breakfast": "Street-side café or hostel breakfast", "lunch": "Local street food stall"},
    "mid":      {"breakfast": "Hotel breakfast buffet", "lunch": "Casual local restaurant"},
    "standard": {"breakfast": "Hotel breakfast or neighborhood bakery", "lunch": "Local bistro or café"},
    "premium":  {"breakfast": "Hotel à la carte breakfast", "lunch": "Upscale casual dining"},
    "luxury":   {"breakfast": "Fine hotel breakfast experience", "lunch": "Michelin-recommended lunch spot"},
}


def _get_cost_tier(destination: str) -> str:
    """Determine the cost tier of a destination."""
    dest_lower = destination.lower().strip()
    tiers = {
        "budget":   ["bangkok", "hanoi", "cairo", "delhi", "lisbon", "krakow"],
        "mid":      ["barcelona", "prague", "budapest", "mexico city", "bali"],
        "standard": ["paris", "rome", "amsterdam", "tokyo", "sydney", "berlin"],
        "premium":  ["london", "new york", "dubai", "singapore", "san francisco"],
        "luxury":   ["monaco", "maldives", "bora bora", "st moritz", "zurich"],
    }
    for tier, cities in tiers.items():
        if any(city in dest_lower for city in cities):
            return tier
    return "standard"


def _is_outdoor(attraction: Attraction) -> bool:
    """Check whether an attraction is outdoor-oriented."""
    if attraction.is_outdoor:
        return True
    attr_type_lower = attraction.type.lower() if attraction.type else ""
    attr_name_lower = attraction.name.lower() if attraction.name else ""
    combined = f"{attr_type_lower} {attr_name_lower}"
    return any(kw in combined for kw in OUTDOOR_KEYWORDS)


def _find_indoor_replacement(
    attractions: list[Attraction],
    used: set[str],
) -> Optional[Attraction]:
    """Find an unused indoor attraction as a swap replacement."""
    for a in attractions:
        if a.name not in used and not _is_outdoor(a):
            return a
    return None


def _weather_for_date(
    weather: WeatherOutput, target_date: date
) -> Optional[DailyForecast]:
    """Look up the forecast for a specific date, or return None."""
    for forecast in weather.daily_forecasts:
        if forecast.date == target_date:
            return forecast
    return None


def build_itinerary(
    destination: str,
    start_date: date,
    end_date: date,
    weather: WeatherOutput,
    discovery: DiscoveryOutput,
    hotel: HotelOutput,
    budget: BudgetOutput,
) -> list[DayPlan]:
    """
    Assemble a complete day-by-day travel itinerary from agent outputs.

    Logic:
    - Distributes attractions: 2 per day, cycling through the list.
    - If a day's forecast has rain_probability > 0.6, swaps outdoor attractions for indoor ones.
    - Assigns 1 hidden gem every other day (days 2, 4, 6...).
    - Rotates restaurants through evening dinner slots.
    - Morning = first attraction or hidden gem.
    - Afternoon = second attraction or free time.
    - Evening = restaurant from list.
    - Meals: breakfast/lunch are generic tier-based; dinner = specific restaurant.
    """
    num_days = (end_date - start_date).days
    if num_days <= 0:
        num_days = 1

    tier = _get_cost_tier(destination)
    meal_defaults = MEAL_SUGGESTIONS.get(tier, MEAL_SUGGESTIONS["standard"])

    # Compute daily spend estimate
    daily_spend = 0.0
    if budget and budget.breakdown:
        non_transport = (
            budget.breakdown.food_usd + budget.breakdown.activities_usd
        )
        daily_spend = non_transport / max(num_days, 1)

    attractions = list(discovery.attractions) if discovery else []
    hidden_gems = list(discovery.hidden_gems) if discovery else []
    restaurants = list(discovery.restaurants) if discovery else []

    used_attractions: set[str] = set()
    attraction_idx = 0
    gem_idx = 0
    restaurant_idx = 0

    days: list[DayPlan] = []

    for day_num in range(1, num_days + 1):
        current_date = start_date + timedelta(days=day_num - 1)
        forecast = _weather_for_date(weather, current_date)

        is_rainy = forecast is not None and forecast.max_rain_probability > 0.6

        # ── Pick morning attraction ──────────────────────────────────
        morning_attraction: Optional[Attraction] = None
        if attraction_idx < len(attractions):
            candidate = attractions[attraction_idx]
            attraction_idx += 1
            if is_rainy and _is_outdoor(candidate):
                replacement = _find_indoor_replacement(attractions, used_attractions)
                if replacement:
                    morning_attraction = replacement
                    used_attractions.add(replacement.name)
                else:
                    morning_attraction = candidate
                    used_attractions.add(candidate.name)
            else:
                morning_attraction = candidate
                used_attractions.add(candidate.name)

        # ── Pick afternoon attraction ────────────────────────────────
        afternoon_attraction: Optional[Attraction] = None
        if attraction_idx < len(attractions):
            candidate = attractions[attraction_idx]
            attraction_idx += 1
            if is_rainy and _is_outdoor(candidate):
                replacement = _find_indoor_replacement(attractions, used_attractions)
                if replacement:
                    afternoon_attraction = replacement
                    used_attractions.add(replacement.name)
                else:
                    afternoon_attraction = candidate
                    used_attractions.add(candidate.name)
            else:
                afternoon_attraction = candidate
                used_attractions.add(candidate.name)

        # ── Hidden gem every other day (days 2, 4, 6…) ───────────────
        hidden_gem: Optional[HiddenGem] = None
        if day_num % 2 == 0 and gem_idx < len(hidden_gems):
            hidden_gem = hidden_gems[gem_idx]
            gem_idx += 1

        # ── Evening restaurant ───────────────────────────────────────
        dinner_restaurant: Optional[Restaurant] = None
        if restaurants:
            dinner_restaurant = restaurants[restaurant_idx % len(restaurants)]
            restaurant_idx += 1

        # ── Build activity descriptions ──────────────────────────────
        morning_activity = ""
        if hidden_gem and not morning_attraction:
            morning_activity = f"Explore hidden gem: {hidden_gem.name}"
        elif morning_attraction:
            morning_activity = f"Visit {morning_attraction.name}"
            if hidden_gem:
                morning_activity += f" + discover hidden gem: {hidden_gem.name}"
        elif hidden_gem:
            morning_activity = f"Explore hidden gem: {hidden_gem.name}"
        else:
            morning_activity = "Free morning — explore the neighborhood"

        afternoon_activity = ""
        if afternoon_attraction:
            afternoon_activity = f"Visit {afternoon_attraction.name}"
        else:
            afternoon_activity = "Free afternoon — relax or explore at your own pace"

        dinner_name = dinner_restaurant.name if dinner_restaurant else "Local restaurant"

        meals = MealPlan(
            breakfast=meal_defaults["breakfast"],
            lunch=meal_defaults["lunch"],
            dinner=f"Dinner at {dinner_name}",
            dinner_restaurant=dinner_restaurant,
        )

        day = DayPlan(
            day_number=day_num,
            date=current_date,
            weather=forecast,
            morning_activity=morning_activity,
            morning_attraction=morning_attraction,
            afternoon_activity=afternoon_activity,
            afternoon_attraction=afternoon_attraction,
            hidden_gem=hidden_gem,
            meals=meals,
            estimated_daily_spend_usd=round(daily_spend, 2),
        )
        days.append(day)

    return days

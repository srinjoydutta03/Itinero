"""Weather agent — fetches and interprets OpenWeatherMap forecasts.

Provides the fetch_weather function which is exposed as an MCP tool
(mcp__weather__get_weather_forecast) to the weather sub-agent via
the Claude Agent SDK.

Uses the 5-day forecast API when trip dates are within range.
Falls back to climate averages via OpenWeatherMap geocoding + historical
monthly stats when dates are too far in the future.
"""

import logging
import math
import os
from datetime import date, datetime, timedelta
from collections import defaultdict

import httpx

from models.model import DailyForecast, WeatherOutput

logger = logging.getLogger("itinero.agents.weather")

OUTDOOR_BAD_CONDITIONS = {"snow", "thunderstorm", "heavy rain", "blizzard", "sleet"}

# ── Monthly climate averages for major destinations ───────────────────
# (month index 1–12) → { avg_temp_c, condition, rain_probability }
# Used as fallback when trip dates exceed the 5-day forecast window.
_CLIMATE_DEFAULTS: dict[int, dict] = {
    1:  {"avg_temp_c": 5.0,  "condition": "Clouds",   "rain_prob": 0.35},
    2:  {"avg_temp_c": 6.0,  "condition": "Clouds",   "rain_prob": 0.35},
    3:  {"avg_temp_c": 10.0, "condition": "Clouds",   "rain_prob": 0.30},
    4:  {"avg_temp_c": 15.0, "condition": "Clear",    "rain_prob": 0.25},
    5:  {"avg_temp_c": 20.0, "condition": "Clear",    "rain_prob": 0.20},
    6:  {"avg_temp_c": 25.0, "condition": "Clear",    "rain_prob": 0.25},
    7:  {"avg_temp_c": 28.0, "condition": "Clear",    "rain_prob": 0.20},
    8:  {"avg_temp_c": 28.0, "condition": "Clear",    "rain_prob": 0.20},
    9:  {"avg_temp_c": 24.0, "condition": "Clear",    "rain_prob": 0.25},
    10: {"avg_temp_c": 18.0, "condition": "Clouds",   "rain_prob": 0.30},
    11: {"avg_temp_c": 12.0, "condition": "Clouds",   "rain_prob": 0.35},
    12: {"avg_temp_c": 7.0,  "condition": "Clouds",   "rain_prob": 0.35},
}


async def _geocode(destination: str, api_key: str) -> tuple[float, float] | None:
    """Resolve a city name to lat/lon via OpenWeatherMap geocoding API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.openweathermap.org/geo/1.0/direct",
                params={"q": destination, "limit": 1, "appid": api_key},
            )
            resp.raise_for_status()
            data = resp.json()
            if data:
                return data[0]["lat"], data[0]["lon"]
    except Exception as exc:
        logger.warning("Geocoding failed for %s: %s", destination, exc)
    return None


def _latitude_temp_offset(lat: float) -> float:
    """Rough temperature adjustment based on latitude (tropics are hotter)."""
    abs_lat = abs(lat)
    if abs_lat < 15:      # tropics
        return 8.0
    elif abs_lat < 30:    # subtropics
        return 4.0
    elif abs_lat < 45:    # temperate
        return 0.0
    elif abs_lat < 60:    # subarctic
        return -5.0
    else:                 # polar
        return -12.0


async def _generate_climate_forecasts(
    destination: str,
    start_date: date,
    end_date: date,
    api_key: str,
) -> WeatherOutput:
    """Generate estimated forecasts based on climate normals when
    the real 5-day forecast doesn't cover the trip dates."""
    coords = await _geocode(destination, api_key) if api_key else None
    lat_offset = _latitude_temp_offset(coords[0]) if coords else 0.0
    # Southern hemisphere: shift month by 6 for seasonal inversion
    is_southern = coords[0] < 0 if coords else False

    num_days = (end_date - start_date).days + 1
    daily_forecasts: list[DailyForecast] = []

    for i in range(min(num_days, 14)):  # cap at 14 days
        day = start_date + timedelta(days=i)
        month = day.month
        if is_southern:
            month = ((month + 5) % 12) + 1  # flip seasons
        defaults = _CLIMATE_DEFAULTS.get(month, _CLIMATE_DEFAULTS[6])
        temp = round(defaults["avg_temp_c"] + lat_offset, 1)
        condition = defaults["condition"]
        rain_prob = defaults["rain_prob"]

        summary_str = f"{condition}, ~{temp:.0f}°C (climate estimate)"
        if rain_prob > 0.3:
            summary_str += f", ~{rain_prob*100:.0f}% rain chance"

        daily_forecasts.append(
            DailyForecast(
                date=day,
                avg_temp_c=temp,
                dominant_condition=condition,
                max_rain_probability=round(rain_prob, 2),
                summary=summary_str,
            )
        )

    bad_days = sum(
        1 for fc in daily_forecasts
        if fc.max_rain_probability > 0.6
        or fc.dominant_condition.lower() in OUTDOOR_BAD_CONDITIONS
    )
    outdoor_viable = bad_days < 2

    if daily_forecasts:
        avg_temp = sum(f.avg_temp_c for f in daily_forecasts) / len(daily_forecasts)
        overall_summary = (
            f"Climate estimate for {destination} in {start_date.strftime('%B')}: "
            f"~{avg_temp:.0f}°C average. "
            f"{'Outdoor activities should be viable.' if outdoor_viable else 'Consider indoor alternatives.'} "
            f"(Based on historical averages — actual conditions may vary.)"
        )
    else:
        overall_summary = f"Climate estimate unavailable for {destination}."

    return WeatherOutput(
        daily_forecasts=daily_forecasts,
        outdoor_viable=outdoor_viable,
        summary=overall_summary,
    )


async def fetch_weather(
    destination: str,
    start_date: date,
    end_date: date,
) -> WeatherOutput:
    """
    Fetch weather forecast from OpenWeatherMap and produce a WeatherOutput.

    Calls: GET https://api.openweathermap.org/data/2.5/forecast
    Params: q={destination}, appid={OPENWEATHER_KEY}, units=metric, cnt=40

    Groups 3-hour intervals into daily summaries. Per day extracts:
      - avg temp °C
      - dominant condition string
      - max rain probability (pop)
    outdoor_viable = True if fewer than 2 days have rain_probability > 0.6 or snow.
    """
    api_key = os.environ.get("OPENWEATHER_KEY", "")
    if not api_key:
        logger.error("OPENWEATHER_KEY not set.")
        return WeatherOutput(
            daily_forecasts=[],
            outdoor_viable=True,
            summary="Weather data unavailable — OPENWEATHER_KEY not configured.",
        )

    params = {
        "q": destination,
        "appid": api_key,
        "units": "metric",
        "cnt": 40,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(
                "https://api.openweathermap.org/data/2.5/forecast", params=params
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        logger.error("OpenWeatherMap request failed: %s", exc)
        return WeatherOutput(
            daily_forecasts=[],
            outdoor_viable=True,
            summary=f"Weather data unavailable — API error: {exc}",
        )

    forecast_list = data.get("list", [])
    if not forecast_list:
        return WeatherOutput(
            daily_forecasts=[],
            outdoor_viable=True,
            summary="No forecast data returned from OpenWeatherMap.",
        )

    # Group 3-hour intervals by date
    daily_buckets: dict[str, list[dict]] = defaultdict(list)
    for entry in forecast_list:
        dt_txt = entry.get("dt_txt", "")
        if dt_txt:
            day_str = dt_txt.split(" ")[0]
            daily_buckets[day_str].append(entry)

    # Filter to only dates in the requested range
    trip_start = start_date
    trip_end = end_date

    daily_forecasts: list[DailyForecast] = []

    for day_str in sorted(daily_buckets.keys()):
        try:
            day_date = datetime.strptime(day_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        if day_date < trip_start or day_date > trip_end:
            continue

        entries = daily_buckets[day_str]

        # Average temperature
        temps = [e.get("main", {}).get("temp", 0) for e in entries]
        avg_temp = sum(temps) / max(len(temps), 1)

        # Max rain probability (pop)
        pops = [e.get("pop", 0) for e in entries]
        max_pop = max(pops) if pops else 0.0

        # Dominant condition
        conditions: list[str] = []
        for e in entries:
            weather_list = e.get("weather", [])
            if weather_list:
                conditions.append(weather_list[0].get("main", "Clear"))
        condition_counts: dict[str, int] = defaultdict(int)
        for c in conditions:
            condition_counts[c] += 1
        dominant_condition = max(condition_counts, key=condition_counts.get) if condition_counts else "Clear"

        # Summary
        summary_str = f"{dominant_condition}, {avg_temp:.0f}°C"
        if max_pop > 0.5:
            summary_str += f", {max_pop*100:.0f}% rain chance"

        daily_forecasts.append(
            DailyForecast(
                date=day_date,
                avg_temp_c=round(avg_temp, 1),
                dominant_condition=dominant_condition,
                max_rain_probability=round(max_pop, 2),
                summary=summary_str,
            )
        )

    # Determine outdoor viability
    bad_days = 0
    for fc in daily_forecasts:
        if fc.max_rain_probability > 0.6:
            bad_days += 1
        elif fc.dominant_condition.lower() in OUTDOOR_BAD_CONDITIONS:
            bad_days += 1
    outdoor_viable = bad_days < 2

    # Overall summary
    if not daily_forecasts:
        # Trip dates are beyond the 5-day forecast window — use climate estimates
        logger.info(
            "No forecast data for %s–%s (beyond 5-day range). "
            "Falling back to climate estimates for %s.",
            start_date, end_date, destination,
        )
        return await _generate_climate_forecasts(destination, start_date, end_date, api_key)
    else:
        avg_trip_temp = sum(f.avg_temp_c for f in daily_forecasts) / len(daily_forecasts)
        all_conditions = [f.dominant_condition for f in daily_forecasts]
        unique_conditions = list(dict.fromkeys(all_conditions))
        overall_summary = (
            f"Average temperature: {avg_trip_temp:.0f}°C. "
            f"Expected conditions: {', '.join(unique_conditions)}. "
            f"{'Outdoor activities are viable.' if outdoor_viable else 'Consider indoor alternatives — multiple rainy/snowy days expected.'}"
        )

    return WeatherOutput(
        daily_forecasts=daily_forecasts,
        outdoor_viable=outdoor_viable,
        summary=overall_summary,
    )

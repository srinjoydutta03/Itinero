"""Transport agent — searches flights via SerpAPI Google Flights.

Provides the search_flights function which is exposed as an MCP tool
(mcp__transport__search_flights) to the transport sub-agent via
the Claude Agent SDK.
"""

import logging
from datetime import date

from models.model import FlightLeg, FlightOption, TransportOutput
from utils.serp_fetch import serp_fetch

logger = logging.getLogger("itinero.agents.transport")

# ── City / airport name → IATA code mapping ──────────────────────────────────
# SerpAPI google_flights requires IATA airport codes for departure_id / arrival_id.
_IATA_CODES: dict[str, str] = {
    # North America
    "new york": "JFK", "nyc": "JFK", "jfk": "JFK", "newark": "EWR",
    "los angeles": "LAX", "la": "LAX", "lax": "LAX",
    "san francisco": "SFO", "sfo": "SFO",
    "chicago": "ORD", "ord": "ORD",
    "miami": "MIA", "mia": "MIA",
    "seattle": "SEA", "sea": "SEA",
    "boston": "BOS", "bos": "BOS",
    "dallas": "DFW", "dfw": "DFW",
    "atlanta": "ATL", "atl": "ATL",
    "denver": "DEN", "den": "DEN",
    "washington": "IAD", "washington dc": "IAD", "dc": "IAD",
    "houston": "IAH", "iah": "IAH",
    "orlando": "MCO", "mco": "MCO",
    "las vegas": "LAS", "las": "LAS",
    "toronto": "YYZ", "yyz": "YYZ",
    "vancouver": "YVR", "yvr": "YVR",
    "montreal": "YUL", "yul": "YUL",
    "mexico city": "MEX", "mex": "MEX",
    # Europe
    "london": "LHR", "lhr": "LHR", "heathrow": "LHR",
    "paris": "CDG", "cdg": "CDG",
    "rome": "FCO", "fco": "FCO",
    "amsterdam": "AMS", "ams": "AMS",
    "frankfurt": "FRA", "fra": "FRA",
    "madrid": "MAD", "mad": "MAD",
    "barcelona": "BCN", "bcn": "BCN",
    "berlin": "BER", "ber": "BER",
    "munich": "MUC", "muc": "MUC",
    "zurich": "ZRH", "zrh": "ZRH",
    "vienna": "VIE", "vie": "VIE",
    "lisbon": "LIS", "lis": "LIS",
    "dublin": "DUB", "dub": "DUB",
    "istanbul": "IST", "ist": "IST",
    "athens": "ATH", "ath": "ATH",
    "milan": "MXP", "mxp": "MXP",
    "prague": "PRG", "prg": "PRG",
    "copenhagen": "CPH", "cph": "CPH",
    "stockholm": "ARN", "arn": "ARN",
    "oslo": "OSL", "osl": "OSL",
    "helsinki": "HEL", "hel": "HEL",
    # Asia
    "tokyo": "NRT", "nrt": "NRT", "narita": "NRT", "haneda": "HND",
    "osaka": "KIX", "kix": "KIX",
    "seoul": "ICN", "icn": "ICN",
    "beijing": "PEK", "pek": "PEK",
    "shanghai": "PVG", "pvg": "PVG",
    "hong kong": "HKG", "hkg": "HKG",
    "bangkok": "BKK", "bkk": "BKK",
    "singapore": "SIN", "sin": "SIN",
    "kuala lumpur": "KUL", "kul": "KUL",
    "mumbai": "BOM", "bom": "BOM",
    "delhi": "DEL", "new delhi": "DEL", "del": "DEL",
    "bangalore": "BLR", "bengaluru": "BLR", "blr": "BLR",
    "taipei": "TPE", "tpe": "TPE",
    "dubai": "DXB", "dxb": "DXB",
    "doha": "DOH", "doh": "DOH",
    "manila": "MNL", "mnl": "MNL",
    "jakarta": "CGK", "cgk": "CGK",
    "hanoi": "HAN", "han": "HAN",
    "ho chi minh": "SGN", "sgn": "SGN", "saigon": "SGN",
    # Oceania
    "sydney": "SYD", "syd": "SYD",
    "melbourne": "MEL", "mel": "MEL",
    "auckland": "AKL", "akl": "AKL",
    # South America
    "sao paulo": "GRU", "gru": "GRU",
    "rio de janeiro": "GIG", "gig": "GIG",
    "buenos aires": "EZE", "eze": "EZE",
    "lima": "LIM", "lim": "LIM",
    "bogota": "BOG", "bog": "BOG",
    # Africa
    "cairo": "CAI", "cai": "CAI",
    "cape town": "CPT", "cpt": "CPT",
    "johannesburg": "JNB", "jnb": "JNB",
    "nairobi": "NBO", "nbo": "NBO",
}


def _resolve_iata(city_or_code: str) -> str:
    """Return an IATA code for the given city name or pass through if already a code."""
    key = city_or_code.strip().lower()
    if key in _IATA_CODES:
        return _IATA_CODES[key]
    # If it looks like an IATA code already (3 uppercase letters), keep it
    stripped = city_or_code.strip()
    if len(stripped) == 3 and stripped.isalpha():
        return stripped.upper()
    logger.warning("Unknown IATA code for '%s', using as-is", city_or_code)
    return stripped


def _parse_flight_options(raw_flights: list[dict]) -> list[FlightOption]:
    """Parse raw SerpAPI flight data into FlightOption models."""
    options: list[FlightOption] = []
    for flight_group in raw_flights:
        price = flight_group.get("price", 0)
        # Price can be a string like "$299" or an int
        if isinstance(price, str):
            price = float(price.replace("$", "").replace(",", "").strip() or "0")
        else:
            price = float(price)

        total_duration = flight_group.get("total_duration", 0)
        flights_data = flight_group.get("flights", [])
        stops = max(len(flights_data) - 1, 0)

        airlines: list[str] = []
        legs: list[FlightLeg] = []
        for seg in flights_data:
            airline = seg.get("airline", "Unknown")
            if airline not in airlines:
                airlines.append(airline)
            legs.append(
                FlightLeg(
                    airline=airline,
                    flight_number=seg.get("flight_number", ""),
                    departure_airport=seg.get("departure_airport", {}).get("id", ""),
                    arrival_airport=seg.get("arrival_airport", {}).get("id", ""),
                    departure_time=seg.get("departure_airport", {}).get("time", ""),
                    arrival_time=seg.get("arrival_airport", {}).get("time", ""),
                    duration_minutes=seg.get("duration", 0),
                )
            )

        if price > 0:
            options.append(
                FlightOption(
                    price_usd=price,
                    airlines=airlines,
                    total_duration_minutes=total_duration,
                    stops=stops,
                    legs=legs,
                )
            )

    return options


async def search_flights(
    origin: str,
    destination: str,
    start_date: date,
    end_date: date,
) -> TransportOutput:
    """
    Search for flights using SerpAPI Google Flights engine.

    Returns the top 3 options sorted by: cheapest, fastest, best_value.
    """
    departure_code = _resolve_iata(origin)
    arrival_code = _resolve_iata(destination)
    logger.info("Searching flights: %s (%s) → %s (%s)", origin, departure_code, destination, arrival_code)

    params = {
        "engine": "google_flights",
        "departure_id": departure_code,
        "arrival_id": arrival_code,
        "outbound_date": start_date.isoformat(),
        "return_date": end_date.isoformat(),
        "currency": "USD",
    }

    data = await serp_fetch(params)

    best_flights = data.get("best_flights", [])
    other_flights = data.get("other_flights", [])
    all_raw = best_flights + other_flights

    if not all_raw:
        logger.warning("No flights found for %s → %s", origin, destination)
        fallback = FlightOption(
            price_usd=0,
            airlines=["No results"],
            total_duration_minutes=0,
            stops=0,
            tag="no_results",
        )
        return TransportOutput(
            options=[],
            recommended=fallback,
            estimated_cost_usd=0,
        )

    options = _parse_flight_options(all_raw)

    if not options:
        fallback = FlightOption(
            price_usd=0,
            airlines=["Parse error"],
            total_duration_minutes=0,
            stops=0,
            tag="parse_error",
        )
        return TransportOutput(
            options=[],
            recommended=fallback,
            estimated_cost_usd=0,
        )

    # ── Score and select top 3 ───────────────────────────────────────────────
    # Normalize price and duration for scoring
    prices = [o.price_usd for o in options]
    durations = [o.total_duration_minutes for o in options if o.total_duration_minutes > 0]

    min_price = min(prices) if prices else 1
    max_price = max(prices) if prices else 1
    price_range = max_price - min_price if max_price != min_price else 1

    min_dur = min(durations) if durations else 1
    max_dur = max(durations) if durations else 1
    dur_range = max_dur - min_dur if max_dur != min_dur else 1

    # Cheapest
    cheapest = min(options, key=lambda o: o.price_usd)
    cheapest.tag = "cheapest"

    # Fastest
    valid_duration = [o for o in options if o.total_duration_minutes > 0]
    fastest = min(valid_duration, key=lambda o: o.total_duration_minutes) if valid_duration else cheapest
    fastest.tag = "fastest"

    # Best value: composite score
    best_value = None
    best_score = -1
    for o in options:
        norm_price = 1 - ((o.price_usd - min_price) / price_range) if price_range else 0.5
        dur = o.total_duration_minutes if o.total_duration_minutes > 0 else max_dur
        norm_dur = 1 - ((dur - min_dur) / dur_range) if dur_range else 0.5
        score = norm_price * 0.6 + norm_dur * 0.4
        if score > best_score:
            best_score = score
            best_value = o
    if best_value:
        best_value.tag = "best_value"
    else:
        best_value = cheapest

    # Deduplicate and collect top 3
    top3_set: dict[float, FlightOption] = {}
    for opt in [cheapest, fastest, best_value]:
        key = (opt.price_usd, opt.total_duration_minutes)
        if key not in top3_set:
            top3_set[key] = opt
    top3 = list(top3_set.values())[:3]

    # Recommended = best_value
    recommended = best_value

    return TransportOutput(
        options=top3,
        recommended=recommended,
        estimated_cost_usd=recommended.price_usd,
    )

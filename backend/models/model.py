"""Pydantic models for the Itinero travel planning system."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ─── Weather Models ──────────────────────────────────────────────────────────

class DailyForecast(BaseModel):
    date: date
    avg_temp_c: float
    dominant_condition: str
    max_rain_probability: float
    summary: str


class WeatherOutput(BaseModel):
    daily_forecasts: list[DailyForecast]
    outdoor_viable: bool
    summary: str


# ─── Transport / Flight Models ───────────────────────────────────────────────

class FlightLeg(BaseModel):
    airline: str
    flight_number: str = ""
    departure_airport: str
    arrival_airport: str
    departure_time: str = ""
    arrival_time: str = ""
    duration_minutes: int = 0


class FlightOption(BaseModel):
    price_usd: float
    airlines: list[str]
    total_duration_minutes: int
    stops: int
    legs: list[FlightLeg] = []
    tag: str = ""  # "cheapest", "fastest", "best_value"


class TransportOutput(BaseModel):
    options: list[FlightOption]
    recommended: FlightOption
    estimated_cost_usd: float


# ─── Hotel Models ────────────────────────────────────────────────────────────

class HotelOption(BaseModel):
    name: str
    total_rate_usd: float
    rate_per_night_usd: float = 0.0
    rating: float = 0.0
    reviews: int = 0
    location: str = ""
    amenities: list[str] = []
    link: str = ""
    value_score: float = 0.0


class HotelOutput(BaseModel):
    options: list[HotelOption]
    recommended: HotelOption
    estimated_total_usd: float


# ─── Discovery Models ───────────────────────────────────────────────────────

class Attraction(BaseModel):
    name: str
    rating: float = 0.0
    reviews: int = 0
    address: str = ""
    type: str = ""
    description: str = ""
    is_outdoor: bool = False


class HiddenGem(BaseModel):
    name: str
    source: str = ""  # "reddit", "google", etc.
    snippet: str = ""
    mentions: int = 1


class Restaurant(BaseModel):
    name: str
    rating: float = 0.0
    address: str = ""
    type: str = ""
    price_level: str = ""
    reviews: int = 0


class DiscoveryOutput(BaseModel):
    attractions: list[Attraction]
    hidden_gems: list[HiddenGem]
    restaurants: list[Restaurant]


# ─── Budget Models ───────────────────────────────────────────────────────────

class CostBreakdown(BaseModel):
    transport_usd: float
    hotel_usd: float
    food_usd: float
    activities_usd: float


class BudgetOutput(BaseModel):
    breakdown: CostBreakdown
    estimated_total_usd: float
    total_budget_usd: float
    remaining_budget_usd: float
    status: Literal["over", "under", "balanced"]
    suggestions: list[str]


# ─── Itinerary Models ───────────────────────────────────────────────────────

class MealPlan(BaseModel):
    breakfast: str = "Hotel breakfast or local café"
    lunch: str = "Local restaurant"
    dinner: str = ""
    dinner_restaurant: Optional[Restaurant] = None


class DayPlan(BaseModel):
    day_number: int
    date: date
    weather: Optional[DailyForecast] = None
    morning_activity: str = ""
    morning_attraction: Optional[Attraction] = None
    afternoon_activity: str = ""
    afternoon_attraction: Optional[Attraction] = None
    hidden_gem: Optional[HiddenGem] = None
    meals: MealPlan = MealPlan()
    estimated_daily_spend_usd: float = 0.0


class DateRange(BaseModel):
    start_date: date
    end_date: date
    num_days: int


# ─── Request / Response Models ───────────────────────────────────────────────

class PlanRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date
    budget_usd: float
    origin: str = "auto"
    travel_style: Literal["affordable", "standard", "premium", "luxury"] = "standard"
    preferences: list[str] = Field(default_factory=list)
    dislikes: list[str] = Field(default_factory=list)


class ReplanRequest(BaseModel):
    session_id: str
    updated_preferences: dict


class TravelPlanResponse(BaseModel):
    session_id: str
    destination: str
    dates: DateRange
    weather: WeatherOutput
    transport: TransportOutput
    hotel: HotelOutput
    discovery: DiscoveryOutput
    budget: BudgetOutput
    itinerary: list[DayPlan]
    agents_run: list[str]
    replanned_agents: list[str]
    errors: list[str]
    llm_summary: str = ""


# ─── Session State ───────────────────────────────────────────────────────────

class SessionState(BaseModel):
    session_id: str
    request: PlanRequest
    weather: Optional[WeatherOutput] = None
    transport: Optional[TransportOutput] = None
    hotel: Optional[HotelOutput] = None
    discovery: Optional[DiscoveryOutput] = None
    budget: Optional[BudgetOutput] = None
    itinerary: list[DayPlan] = Field(default_factory=list)
    agents_run: list[str] = Field(default_factory=list)
    replanned_agents: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    llm_summary: Optional[str] = None
    updated_at: Optional[datetime] = None


# ─── Chat Models ─────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    """A single message in a chat conversation."""
    role: Literal["user", "assistant"]
    content: str
    timestamp: Optional[datetime] = None
    events: list[dict] = Field(default_factory=list)


class ChatRequest(BaseModel):
    """Request body for the /api/chat endpoint."""
    session_id: Optional[str] = None  # None = start new chat session
    message: str


class ChatResponse(BaseModel):
    """Response from the /api/chat endpoint."""
    session_id: str
    reply: str
    events: list[dict] = Field(default_factory=list)
    agent_summary: Optional[dict] = None
    updated_plan: Optional[dict] = None  # Full TravelPlanResponse when chat triggers agent updates

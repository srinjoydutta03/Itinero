/**
 * Frontend TypeScript types mirroring the backend Pydantic models.
 * See: backend/models/model.py
 */

// ─── Weather ────────────────────────────────────────────────────────────────

export interface DailyForecast {
  date: string; // ISO date string
  avg_temp_c: number;
  dominant_condition: string;
  max_rain_probability: number;
  summary: string;
}

export interface WeatherOutput {
  daily_forecasts: DailyForecast[];
  outdoor_viable: boolean;
  summary: string;
}

// ─── Transport / Flights ────────────────────────────────────────────────────

export interface FlightLeg {
  airline: string;
  flight_number: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
}

export interface FlightOption {
  price_usd: number;
  airlines: string[];
  total_duration_minutes: number;
  stops: number;
  legs: FlightLeg[];
  tag: string; // "cheapest" | "fastest" | "best_value"
}

export interface TransportOutput {
  options: FlightOption[];
  recommended: FlightOption;
  estimated_cost_usd: number;
}

// ─── Hotels ─────────────────────────────────────────────────────────────────

export interface HotelOption {
  name: string;
  total_rate_usd: number;
  rate_per_night_usd: number;
  rating: number;
  reviews: number;
  location: string;
  amenities: string[];
  link: string;
  value_score: number;
}

export interface HotelOutput {
  options: HotelOption[];
  recommended: HotelOption;
  estimated_total_usd: number;
}

// ─── Discovery ──────────────────────────────────────────────────────────────

export interface Attraction {
  name: string;
  rating: number;
  reviews: number;
  address: string;
  type: string;
  description: string;
  is_outdoor: boolean;
}

export interface HiddenGem {
  name: string;
  source: string;
  snippet: string;
  mentions: number;
}

export interface Restaurant {
  name: string;
  rating: number;
  address: string;
  type: string;
  price_level: string;
  reviews: number;
}

export interface DiscoveryOutput {
  attractions: Attraction[];
  hidden_gems: HiddenGem[];
  restaurants: Restaurant[];
}

// ─── Budget ─────────────────────────────────────────────────────────────────

export interface CostBreakdown {
  transport_usd: number;
  hotel_usd: number;
  food_usd: number;
  activities_usd: number;
}

export interface BudgetOutput {
  breakdown: CostBreakdown;
  estimated_total_usd: number;
  total_budget_usd: number;
  remaining_budget_usd: number;
  status: "over" | "under" | "balanced";
  suggestions: string[];
}

// ─── Itinerary ──────────────────────────────────────────────────────────────

export interface MealPlan {
  breakfast: string;
  lunch: string;
  dinner: string;
  dinner_restaurant?: Restaurant | null;
}

export interface DayPlan {
  day_number: number;
  date: string;
  weather?: DailyForecast | null;
  morning_activity: string;
  morning_attraction?: Attraction | null;
  afternoon_activity: string;
  afternoon_attraction?: Attraction | null;
  hidden_gem?: HiddenGem | null;
  meals: MealPlan;
  estimated_daily_spend_usd: number;
}

export interface DateRange {
  start_date: string;
  end_date: string;
  num_days: number;
}

// ─── API Request / Response Models ──────────────────────────────────────────

export interface PlanRequest {
  destination: string;
  start_date: string; // ISO date YYYY-MM-DD
  end_date: string;
  budget_usd: number;
  origin: string;
  travel_style: "affordable" | "standard" | "premium" | "luxury";
  preferences: string[];
  dislikes: string[];
}

export interface TravelPlanResponse {
  session_id: string;
  destination: string;
  dates: DateRange;
  weather: WeatherOutput;
  transport: TransportOutput;
  hotel: HotelOutput;
  discovery: DiscoveryOutput;
  budget: BudgetOutput;
  itinerary: DayPlan[];
  agents_run: string[];
  replanned_agents: string[];
  errors: string[];
  llm_summary: string;
}

export interface ReplanRequest {
  session_id: string;
  updated_preferences: Record<string, unknown>;
}

// ─── Chat Models ────────────────────────────────────────────────────────────

export interface ChatRequest {
  session_id?: string | null;
  message: string;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  events: Record<string, unknown>[];
  agent_summary?: Record<string, unknown> | null;
  updated_plan?: TravelPlanResponse | null;
}

// ─── Trip form data passed from Home → Dashboard ────────────────────────────

export interface TripFormData {
  origin: string;
  destination: string;
  startDate: string; // ISO date
  endDate: string;
  travelers: number;
  budget: number;
  travel_style: "affordable" | "standard" | "premium" | "luxury";
  preferences: string[];
  dislikes: string[];
}

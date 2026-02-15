"""Budget agent — aggregates costs and optimises against the total budget.

Provides the optimize_budget function which is exposed as an MCP tool
(mcp__budget__optimize_budget) to the budget sub-agent via
the Claude Agent SDK.

Travel style multipliers (applied to the stated budget):
  - affordable  → target 80% of budget  (save money)
  - standard    → target 100% of budget (use it all wisely)
  - premium     → target 120% of budget (willing to stretch)
  - luxury      → no ceiling            (spend freely)

Food and activity costs are *derived* from the effective budget rather
than hardcoded per-city.  After subtracting fixed costs (transport +
hotel) from the effective budget, the remainder is split:
  - 60% food
  - 40% activities / experiences
"""

import logging

from models.model import BudgetOutput, CostBreakdown

logger = logging.getLogger("itinero.agents.budget")

# Multiplier applied to the stated budget to get the planning ceiling.
# Luxury has no cap — we set the multiplier very high so the math
# works but the status is always "balanced".
STYLE_MULTIPLIERS: dict[str, float] = {
    "affordable": 0.80,
    "standard": 1.00,
    "premium": 1.20,
    "luxury": 999.0,  # effectively uncapped
}

# Minimum per-day food & activity floors so estimates stay realistic
# even when the budget is extremely tight.
MIN_FOOD_PER_DAY = 15.0
MIN_ACTIVITIES_PER_DAY = 5.0


async def optimize_budget(
    transport_cost: float,
    hotel_cost: float,
    destination: str,
    num_days: int,
    total_budget: float,
    travel_style: str = "standard",
) -> BudgetOutput:
    """
    Aggregate all cost components, compare against budget, and generate
    suggestions.

    Food and activity costs are *derived* from the budget:
      effective_budget = total_budget × style_multiplier
      discretionary   = effective_budget − transport − hotel
      food            = discretionary × 0.60
      activities      = discretionary × 0.40

    Status thresholds are measured against the effective budget.
    """
    if num_days <= 0:
        num_days = 1

    style = travel_style.lower().strip()
    multiplier = STYLE_MULTIPLIERS.get(style, 1.0)
    is_luxury = style == "luxury"

    effective_budget = total_budget * multiplier

    # Discretionary = what's left after fixed transport + hotel costs
    discretionary = max(effective_budget - transport_cost - hotel_cost, 0)

    # Split discretionary: 60 % food, 40 % activities
    food_cost = max(discretionary * 0.60, MIN_FOOD_PER_DAY * num_days)
    activities_cost = max(discretionary * 0.40, MIN_ACTIVITIES_PER_DAY * num_days)

    estimated_total = transport_cost + hotel_cost + food_cost + activities_cost
    remaining = total_budget - estimated_total

    # ── Status ───────────────────────────────────────────────────────────
    if is_luxury:
        status = "balanced"  # luxury never flags as over
    elif estimated_total > effective_budget * 1.05:
        status = "over"
    elif estimated_total < effective_budget * 0.80:
        status = "under"
    else:
        status = "balanced"

    # ── Suggestions ──────────────────────────────────────────────────────
    suggestions = _generate_suggestions(
        status=status,
        transport_cost=transport_cost,
        hotel_cost=hotel_cost,
        food_cost=food_cost,
        activities_cost=activities_cost,
        estimated_total=estimated_total,
        total_budget=total_budget,
        effective_budget=effective_budget,
        remaining=remaining,
        num_days=num_days,
        travel_style=style,
        destination=destination,
        is_luxury=is_luxury,
    )

    breakdown = CostBreakdown(
        transport_usd=round(transport_cost, 2),
        hotel_usd=round(hotel_cost, 2),
        food_usd=round(food_cost, 2),
        activities_usd=round(activities_cost, 2),
    )

    return BudgetOutput(
        breakdown=breakdown,
        estimated_total_usd=round(estimated_total, 2),
        total_budget_usd=round(total_budget, 2),
        remaining_budget_usd=round(remaining, 2),
        status=status,
        suggestions=suggestions,
    )


def _generate_suggestions(
    status: str,
    transport_cost: float,
    hotel_cost: float,
    food_cost: float,
    activities_cost: float,
    estimated_total: float,
    total_budget: float,
    effective_budget: float,
    remaining: float,
    num_days: int,
    travel_style: str,
    destination: str,
    is_luxury: bool,
) -> list[str]:
    """Generate actionable budget suggestions based on status and style."""
    suggestions: list[str] = []
    overage = estimated_total - total_budget
    style_label = travel_style.capitalize()
    food_per_day = food_cost / max(num_days, 1)
    activities_per_day = activities_cost / max(num_days, 1)

    if is_luxury:
        suggestions.append(
            f"Luxury style — no budget ceiling. Estimated spend: "
            f"${estimated_total:,.0f} for {num_days} days in {destination}."
        )
        suggestions.append(
            f"Dining: ~${food_per_day:,.0f}/day · Experiences: ~${activities_per_day:,.0f}/day. "
            f"Consider Michelin-starred restaurants, private tours, and premium transfers."
        )
        if remaining > 0:
            suggestions.append(
                f"You still have ${remaining:,.0f} of your stated ${total_budget:,.0f} budget available."
            )
        return suggestions

    if status == "over":
        suggestions.append(
            f"{style_label} plan is ${abs(overage):,.0f} over your ${total_budget:,.0f} budget. "
            f"Ways to bring it down:"
        )

        if transport_cost > total_budget * 0.35:
            suggestions.append(
                f"Flights (${transport_cost:,.0f}) consume {transport_cost/total_budget*100:.0f}% "
                f"of your budget. Try economy class, flexible dates, or alternate airports."
            )

        avg_nightly = hotel_cost / max(num_days, 1)
        if hotel_cost > total_budget * 0.30:
            suggestions.append(
                f"Hotel (${hotel_cost:,.0f}, ~${avg_nightly:,.0f}/night) is a major expense. "
                f"Consider a neighboring district or a well-rated 3-star option."
            )

        suggestions.append(
            f"Dining is estimated at ~${food_per_day:,.0f}/day. Eat breakfast at the "
            f"hotel and choose local lunch spots to save."
        )

    elif status == "under":
        suggestions.append(
            f"{style_label} plan uses ${estimated_total:,.0f} of ${total_budget:,.0f} — "
            f"you have ${remaining:,.0f} to spare. Upgrade ideas:"
        )

        upgrade_per_night = remaining * 0.4 / max(num_days, 1)
        suggestions.append(
            f"Upgrade your hotel by ~${upgrade_per_night:,.0f}/night for a better "
            f"location or amenities."
        )
        suggestions.append(
            f"Add a premium experience: private guided tour, fine-dining reservation, "
            f"or a day trip from {destination} (~${remaining * 0.25:,.0f})."
        )

    else:
        suggestions.append(
            f"{style_label} plan is well-balanced at ${estimated_total:,.0f} against "
            f"a ${total_budget:,.0f} budget "
            f"(effective target: ${effective_budget:,.0f})."
        )
        suggestions.append(
            f"Dining: ~${food_per_day:,.0f}/day · Experiences: ~${activities_per_day:,.0f}/day."
        )

    return suggestions

import logging
from typing import List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Risk score thresholds
_LOW_MAX = 3
_MEDIUM_MAX = 6


@dataclass
class RiskProfile:
    score: int
    level: str          # "Low" | "Medium" | "Higher"
    factors: List[str]  # Human-readable list of rules that fired


def evaluate_risk(
    time_of_day: str,
    commute_distance_km: float,
    living_arrangement: str,
    safety_tolerance: str,
    budget_kes: float,
) -> RiskProfile:
    """
    Apply deterministic rules to produce a situational risk profile.
    This function must NOT call the AI — all logic is rule-based.

    Rules:
        - Night return adds 2 points (higher exposure after dark)
        - Commute > 5km adds 1 point (longer exposure window)
        - Commute > 10km adds 1 more point
        - Living alone adds 1 point (no immediate support at home)
        - Low safety tolerance adds 1 point (user is more risk-averse)
        - Budget < 10,000 KES adds 1 point (limits access to secured housing)
    """
    score = 0
    factors = []

    time_lower = time_of_day.lower()
    if any(t in time_lower for t in ["night", "late", "evening", "midnight"]):
        score += 2
        factors.append("Returns home at night — higher exposure after dark")

    if commute_distance_km > 10:
        score += 2
        factors.append(f"Long commute of {commute_distance_km}km — extended time in transit")
    elif commute_distance_km > 5:
        score += 1
        factors.append(f"Moderate commute of {commute_distance_km}km")

    if living_arrangement.lower() in ["alone", "single", "solo"]:
        score += 1
        factors.append("Living alone — no immediate support at home")

    if safety_tolerance.lower() == "low":
        score += 1
        factors.append("Low safety tolerance — stricter neighborhood filters applied")

    if budget_kes < 10000:
        score += 1
        factors.append("Budget under KES 10,000 — may limit access to secured housing options")

    if score <= _LOW_MAX:
        level = "Low"
    elif score <= _MEDIUM_MAX:
        level = "Medium"
    else:
        level = "Higher"

    logger.info(f"Risk evaluation: score={score}, level={level}, factors={factors}")
    return RiskProfile(score=score, level=level, factors=factors)

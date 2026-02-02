
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from enum import Enum


class RiskTolerance(Enum):
    """User's personal risk tolerance level."""
    LOW = "low"       # Prefers shorter commutes, earlier returns, more populated areas
    MEDIUM = "medium" # Comfortable with moderate trade-offs
    HIGH = "high"     # Longer commutes, later returns acceptable


class ReturnTime(Enum):
    """Typical return time to home."""
    DAYTIME = "daytime"  # Before 6 PM
    EVENING = "evening"  # 6 PM - 9 PM
    NIGHT = "night"      # After 9 PM


class LivingArrangement(Enum):
    """Living arrangement type."""
    ALONE = "alone"
    SHARED = "shared"
    FAMILY = "family"


class TransportMode(Enum):
    """Modes of transportation available."""
    WALKING = "walking"
    BODABODA = "bodaboda"
    MATATU = "matatu"
    PRIVATE = "private"
    BUS = "bus"


class RiskLevel(Enum):
    """Risk level classification (situational, not area-based)."""
    LOW = "low"
    MODERATE = "moderate"
    ELEVATED = "elevated"

    def description(self) -> str:
        descriptions = {
            RiskLevel.LOW: "Standard precautions apply",
            RiskLevel.MODERATE: "Additional awareness recommended",
            RiskLevel.ELEVATED: "Consider adjusting commute or timing"
        }
        return descriptions.get(self, "")


class HousingRequirements(BaseModel):
    has_all_details: bool
    current_location: Optional[str] = ""
    target_location: Optional[str] = ""
    workplace_location: Optional[str] = ""
    monthly_budget: Optional[float] = 0
    preferences: Optional[str] = ""
    # New situational factors for ethical safety recommendations
    risk_tolerance: Optional[RiskTolerance] = RiskTolerance.MEDIUM
    typical_return_time: Optional[ReturnTime] = ReturnTime.EVENING
    living_arrangement: Optional[LivingArrangement] = LivingArrangement.ALONE
    transport_mode: Optional[TransportMode] = TransportMode.MATATU
    commute_minutes: Optional[int] = 30
    familiar_with_area: Optional[bool] = False
    has_night_activities: Optional[bool] = False


class ContextualSafetyFactors(BaseModel):
    """Objective safety factors for a neighborhood - NOT labels, but conditions."""
    street_lighting: Optional[str] = ""  # "good", "partial", "limited"
    night_pedestrian_activity: Optional[str] = ""  # "high", "moderate", "low"
    public_transport_hours: Optional[str] = ""  # "24/7", "6am-10pm", "limited"
    community_watch: Optional[bool] = False
    local_initiatives: Optional[List[str]] = []  # What residents are doing


class TimeSafetyProfile(BaseModel):
    """Safety profile at different times of day."""
    morning_commute_safety: Optional[str] = ""  # Based on daylight, traffic
    evening_commute_safety: Optional[str] = ""  # Based on lighting, activity
    night_safety: Optional[str] = ""  # Separate from day safety
    weekend_patterns: Optional[str] = ""  # Different from weekday


class CommunityStrategies(BaseModel):
    """Security measures residents actually use - empowerment-focused."""
    digital_safety: Optional[List[str]] = []  # mobile payment apps, ride-hailing
    physical_safety: Optional[List[str]] = []  # well-lit groups, safe houses
    transport_safety: Optional[List[str]] = []  # verified boda-boda, women-only matatus
    community_resources: Optional[List[str]] = []  # WhatsApp groups, associations


class PersonalSafetyChecklist(BaseModel):
    """Personalized safety strategies based on user profile."""
    route_options: Optional[List[str]] = []  # Alternative routes with better lighting
    timing_suggestions: Optional[List[str]] = []  # Shift commute by 30 minutes
    tech_solutions: Optional[List[str]] = []  # Safety apps, emergency contacts
    community_resources: Optional[List[str]] = []  # Join neighborhood group


class Neighborhood(BaseModel):
    name: str
    distance_to_cbd: Optional[str] = ""
    distance_to_workplace: Optional[str] = ""
    average_rent_1br: Optional[str] = ""
    average_rent_2br: Optional[str] = ""
    transportation: Optional[str] = ""
    amenities: Optional[List[str]] = []
    description: Optional[str] = ""
    key_tradeoffs: Optional[str] = ""
    factors_to_consider: Optional[List[str]] = []
    general_notes: Optional[str] = ""
    # New ethical safety fields
    contextual_factors: Optional[ContextualSafetyFactors] = None
    time_profile: Optional[TimeSafetyProfile] = None
    community_strategies: Optional[CommunityStrategies] = None
    personal_checklist: Optional[PersonalSafetyChecklist] = None
    comparative_context: Optional[str] = ""  # Relative to other areas


class NeighborhoodRecommendation(BaseModel):
    neighborhoods: List[Neighborhood]


class Message(TypedDict):
    role: str
    content: str

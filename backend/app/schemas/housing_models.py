
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class HousingRequirements(BaseModel):
    has_all_details: bool
    current_location: Optional[str] = ""
    target_location: Optional[str] = ""
    workplace_location: Optional[str] = ""
    monthly_budget: Optional[float] = 0
    preferences: Optional[str] = ""


class Neighborhood(BaseModel):
    name: str
    distance_to_cbd: str
    average_rent_1br: str
    average_rent_2br: str
    security_rating: str
    security_details: str
    amenities: List[str]
    transportation: str
    description: str
    pros: List[str]
    cons: List[str]


class NeighborhoodRecommendation(BaseModel):
    neighborhoods: List[Neighborhood]


class Message(TypedDict):
    role: str
    content: str
"""
Rule-Based Risk Evaluation Engine

This module provides deterministic, rule-based evaluation of situational risk factors
based on Documentation-guide principles:
- Rule-driven with AI-assisted explanation
- Focused on trade-offs, not predictions
- Minimal but structured data

The engine does NOT:
- Use real crime data
- Label neighborhoods as "safe" or "dangerous"
- Make predictions about safety outcomes

The engine DOES:
- Apply predefined rules to user profile
- Produce situational risk scores
- Focus on factors the user can control (commute, timing, transport)
- Respect user's personal risk tolerance
- Provide empowerment-focused recommendations

Key Ethical Principles:
1. Risk tolerance is USER-DEFINED, not area-based
2. Same location can be appropriate for high-tolerance user but not low-tolerance
3. Focus on actionable strategies, not labels
4. Compare factors, not areas
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
from src.models.housing_models import RiskTolerance, ReturnTime, LivingArrangement, TransportMode
import time


class TransportMode(Enum):
    """Modes of transportation available."""
    WALKING = "walking"
    BODABODA = "bodaboda"
    MATATU = "matatu"
    PRIVATE = "private"
    BUS = "bus"


class ReturnTime(Enum):
    """Typical return time to home."""
    DAYTIME = "daytime"  # Before 6 PM
    EVENING = "evening"  # 6 PM - 9 PM
    NIGHT = "night"  # After 9 PM


class LivingArrangement(Enum):
    """Living arrangement type."""
    ALONE = "alone"
    SHARED = "shared"
    FAMILY = "family"


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


@dataclass
class RiskFactor:
    """Represents a single risk factor with its evaluation."""
    factor_name: str
    description: str
    risk_level: RiskLevel
    mitigation_suggestion: str


@dataclass
class RiskProfile:
    """Complete risk evaluation profile."""
    overall_risk_level: RiskLevel
    risk_factors: List[RiskFactor]
    key_considerations: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "overall_risk_level": self.overall_risk_level.value,
            "risk_factors": [
                {
                    "factor": f.factor_name,
                    "description": f.description,
                    "level": f.risk_level.value,
                    "mitigation": f.mitigation_suggestion
                }
                for f in self.risk_factors
            ],
            "key_considerations": self.key_considerations,
            "recommendations": self.recommendations
        }


class RiskEngine:
    """
    Deterministic rule-based risk evaluation engine.
    
    Rules are based on:
    - Commute duration
    - Return time
    - Transport mode
    - Living arrangement
    - Familiarity with area
    """
    
    def __init__(self):
        """Initialize the risk engine with rule definitions."""
        self._rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict:
        """
        Initialize rule definitions.
        
        Rules follow the pattern:
        - condition: function that evaluates the condition
        - factor: name of the risk factor
        - description: what the factor is about
        - mitigation: suggestion for reducing risk
        """
        return [
            {
                "id": "commute_duration",
                "name": "Long Commute Duration",
                "check": lambda ctx: ctx.get("commute_minutes", 0) > 60,
                "description": "Long commute times increase exposure to various situations",
                "mitigation": "Consider options closer to workplace or adjust timing",
                "elevated_threshold": 90,
                "moderate_threshold": 45,
            },
            {
                "id": "night_return",
                "name": "Night Return Time",
                "check": lambda ctx: ctx.get("return_time") == ReturnTime.NIGHT,
                "description": "Returning late at night may have different considerations",
                "mitigation": "Plan reliable transport options in advance",
            },
            {
                "id": "evening_return",
                "name": "Evening Return Time",
                "check": lambda ctx: ctx.get("return_time") == ReturnTime.EVENING,
                "description": "Evening returns may have different transport availability",
                "mitigation": "Check matatu/bus schedules for evening availability",
            },
            {
                "id": "walking_commute",
                "name": "Walking as Primary Transport",
                "check": lambda ctx: ctx.get("transport_mode") == TransportMode.WALKING,
                "description": "Walking entire commute depends on distance and route",
                "mitigation": "Ensure route is well-lit and populated during your travel times",
            },
            {
                "id": "bodaboda_commute",
                "name": "Bodaboda Transport",
                "check": lambda ctx: ctx.get("transport_mode") == TransportMode.BODABODA,
                "description": "Bodaboda transport is common but safety depends on helmet use and rider behavior",
                "mitigation": "Always wear helmet, agree on fare before riding",
            },
            {
                "id": "alone_living",
                "name": "Living Alone",
                "check": lambda ctx: ctx.get("living_arrangement") == LivingArrangement.ALONE,
                "description": "Living alone means no immediate household support",
                "mitigation": "Establish local contacts and emergency contacts",
            },
            {
                "id": "new_area",
                "name": "New to Area",
                "check": lambda ctx: not ctx.get("familiar_with_area", True),
                "description": "Unfamiliarity with an area means learning local norms and routes",
                "mitigation": "Spend time exploring the area during daytime first",
            },
            {
                "id": "budget_tight",
                "name": "Tight Budget Constraints",
                "check": lambda ctx: ctx.get("budget_comfort", 1.0) < 0.7,
                "description": "Very tight budgets may limit housing options to less central areas",
                "mitigation": "Consider commute trade-offs vs housing quality",
            },
        ]
    
    def evaluate(
        self,
        commute_minutes: int = 30,
        return_time: ReturnTime = ReturnTime.EVENING,
        transport_mode: TransportMode = TransportMode.MATATU,
        living_arrangement: LivingArrangement = LivingArrangement.ALONE,
        familiar_with_area: bool = False,
        budget_comfort: float = 0.5,  # 0-1 scale
        has_night_activities: bool = False,
        risk_tolerance: RiskTolerance = RiskTolerance.MEDIUM,
    ) -> RiskProfile:
        """
        Evaluate risk based on user profile and context.
        
        KEY: The risk tolerance is USER-DEFINED. The same location may be
        appropriate for a HIGH tolerance user but not for a LOW tolerance user.
        This avoids labeling areas and respects user autonomy.
        
        Args:
            commute_minutes: Daily commute time in minutes
            return_time: Typical return time category
            transport_mode: Primary mode of transport
            living_arrangement: Living alone/shared/family
            familiar_with_area: Whether familiar with the area
            budget_comfort: How comfortable budget is (0-1 scale)
            has_night_activities: Whether regularly out at night
            risk_tolerance: User's personal risk tolerance (LOW/MEDIUM/HIGH)
            
        Returns:
            RiskProfile with evaluation results
        """
        # Build context dictionary
        context = {
            "commute_minutes": commute_minutes,
            "return_time": return_time,
            "transport_mode": transport_mode,
            "living_arrangement": living_arrangement,
            "familiar_with_area": familiar_with_area,
            "budget_comfort": budget_comfort,
            "has_night_activities": has_night_activities,
            "risk_tolerance": risk_tolerance,
        }
        
        # Evaluate all rules
        risk_factors = []
        for rule in self._rules:
            try:
                if rule["check"](context):
                    # Determine risk level based on thresholds
                    risk_level = self._determine_risk_level(rule, context)
                    
                    risk_factors.append(RiskFactor(
                        factor_name=rule["name"],
                        description=rule["description"],
                        risk_level=risk_level,
                        mitigation_suggestion=rule["mitigation"]
                    ))
            except (TypeError, KeyError):
                # Skip rules with missing context
                continue
        
        # Calculate overall risk level
        overall_level = self._calculate_overall_risk(risk_factors)
        
        # Generate key considerations
        considerations = self._generate_considerations(risk_factors, context)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_factors, context)
        
        return RiskProfile(
            overall_risk_level=overall_level,
            risk_factors=risk_factors,
            key_considerations=considerations,
            recommendations=recommendations
        )
    
    def _determine_risk_level(self, rule: Dict, context: Dict) -> RiskLevel:
        """Determine the risk level for a triggered rule."""
        # For commute duration, use thresholds
        if rule["id"] == "commute_duration":
            commute = context.get("commute_minutes", 0)
            elevated_threshold = rule.get("elevated_threshold", 90)
            moderate_threshold = rule.get("moderate_threshold", 45)
            
            if commute > elevated_threshold:
                return RiskLevel.ELEVATED
            elif commute > moderate_threshold:
                return RiskLevel.MODERATE
            else:
                return RiskLevel.LOW
        
        # For other rules, default to MODERATE when triggered
        return RiskLevel.MODERATE
    
    def _calculate_overall_risk(self, risk_factors: List[RiskFactor]) -> RiskLevel:
        """Calculate overall risk level from all factors."""
        if not risk_factors:
            return RiskLevel.LOW
        
        # Count factors by level
        elevated_count = sum(1 for f in risk_factors if f.risk_level == RiskLevel.ELEVATED)
        moderate_count = sum(1 for f in risk_factors if f.risk_level == RiskLevel.MODERATE)
        
        # Determine overall level
        if elevated_count >= 2:
            return RiskLevel.ELEVATED
        elif elevated_count >= 1 or moderate_count >= 3:
            return RiskLevel.MODERATE
        elif moderate_count >= 1:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _generate_considerations(
        self, 
        risk_factors: List[RiskFactor], 
        context: Dict
    ) -> List[str]:
        """Generate key considerations based on risk factors."""
        considerations = []
        
        # Add considerations based on triggered rules
        for factor in risk_factors:
            if factor.risk_level == RiskLevel.ELEVATED:
                considerations.append(f"⚠️  {factor.factor_name}: {factor.description}")
            else:
                considerations.append(f"• {factor.factor_name}: {factor.description}")
        
        return considerations
    
    def _generate_recommendations(
        self, 
        risk_factors: List[RiskFactor], 
        context: Dict
    ) -> List[str]:
        """
        Generate empowerment-focused recommendations based on risk factors.
        
        Uses positive framing: "Consider these strategies" not "Avoid this"
        """
        recommendations = []
        
        for factor in risk_factors:
            recommendations.append(f"• {factor.mitigation_suggestion}")
        
        # Add empowerment-focused general recommendations
        recommendations.extend([
            # Transport safety
            "• Consider verified ride-hailing services for late-night travel",
            "• Research women-only matatu options if applicable",
            "• Always agree on fares before using bodaboda",
            # Digital safety
            "• Use mobile payment apps to minimize cash handling",
            "• Share your travel itinerary with a trusted contact",
            "• Keep phone charged and emergency numbers saved",
            # Community resources
            "• Join local neighborhood WhatsApp groups for real-time info",
            "• Connect with residents' association for community updates",
            "• Explore the area during daytime to build familiarity",
        ])
        
        return recommendations
    
    def compare_options(
        self,
        options: List[Dict]
    ) -> List[Dict]:
        """
        Compare multiple housing options based on risk factors.
        
        Args:
            options: List of housing options with commute info
            
        Returns:
            List of options with risk evaluation added
        """
        results = []
        
        for option in options:
            commute = option.get("commute_minutes", 30)
            transport = option.get("transport_mode", TransportMode.MATATU)
            
            # Evaluate this option
            profile = self.evaluate(
                commute_minutes=commute,
                return_time=ReturnTime.EVENING,
                transport_mode=transport,
                living_arrangement=LivingArrangement.ALONE,
                familiar_with_area=False,
            )
            
            # Add to result
            result = {
                "name": option.get("name", "Unknown"),
                "commute_minutes": commute,
                "transport_mode": transport.value,
                "risk_evaluation": profile.to_dict(),
                "trade_offs": self._generate_option_tradeoffs(option, profile)
            }
            
            results.append(result)
        
        return results
    
    def _generate_option_tradeoffs(
        self, 
        option: Dict, 
        profile: RiskProfile
    ) -> str:
        """Generate a summary of trade-offs for an option."""
        tradeoffs = []
        
        # Cost vs commute tradeoff
        commute = option.get("commute_minutes", 30)
        rent = option.get("rent_kes", 0)
        
        if commute > 45 and rent < 50000:
            tradeoffs.append("Lower rent but longer commute")
        elif commute < 30 and rent > 80000:
            tradeoffs.append("Shorter commute but higher rent")
        else:
            tradeoffs.append("Balanced cost and commute")
        
        # Transport considerations
        transport = option.get("transport_mode", "")
        if transport == "walking":
            tradeoffs.append("Walking access - good for health, depends on distance")
        elif transport == "matatu":
            tradeoffs.append("Matatu access - affordable, schedule-dependent")
        elif transport == "private":
            tradeoffs.append("Private transport - flexible but higher cost")
        
        return "; ".join(tradeoffs)


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("RULE-BASED RISK EVALUATION ENGINE")
    print("=" * 80)
    
    engine = RiskEngine()
    
    # Example evaluation
    profile = engine.evaluate(
        commute_minutes=75,
        return_time=ReturnTime.NIGHT,
        transport_mode=TransportMode.MATATU,
        living_arrangement=LivingArrangement.ALONE,
        familiar_with_area=False,
        budget_comfort=0.4,
    )
    
    print(f"\nOverall Risk Level: {profile.overall_risk_level.value.upper()}")
    print(f"\nRisk Factors ({len(profile.risk_factors)}):")
    for factor in profile.risk_factors:
        print(f"  - {factor.factor_name}: {factor.risk_level.value}")
        print(f"    {factor.description}")
        print(f"    → {factor.mitigation_suggestion}")
    
    print(f"\nKey Considerations:")
    for consideration in profile.key_considerations:
        print(f"  {consideration}")
    
    print(f"\nRecommendations:")
    for rec in profile.recommendations[:4]:
        print(f"  {rec}")


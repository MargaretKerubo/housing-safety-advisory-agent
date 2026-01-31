"""
Trade-off Analyzer

Aggregates rule outputs and balances safety vs cost vs convenience
to produce comparable option scores.

Based on Documentation-guide principles:
- Focused on trade-offs, not predictions
- Explainable decision-making
- Advisory, not authoritative
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math


class Priority(Enum):
    """User priority levels for trade-off analysis."""
    SAFETY_CONCERNS = "safety_concerns"
    COST = "cost"
    COMMUTE = "commute"
    AMENITIES = "amenities"
    TRANSPORT = "transport"


@dataclass
class TradeOffScore:
    """Score breakdown for a single housing option."""
    option_name: str
    total_score: float
    cost_score: float
    commute_score: float
    convenience_score: float
    priority_scores: Dict[str, float]
    strengths: List[str]
    trade_offs: List[str]
    warnings: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "option_name": self.option_name,
            "total_score": round(self.total_score, 2),
            "scores": {
                "cost": round(self.cost_score, 2),
                "commute": round(self.commute_score, 2),
                "convenience": round(self.convenience_score, 2),
            },
            "priority_scores": {k: round(v, 2) for k, v in self.priority_scores.items()},
            "strengths": self.strengths,
            "trade_offs": self.trade_offs,
            "warnings": self.warnings
        }


@dataclass
class TradeOffComparison:
    """Comparison of multiple housing options."""
    options: List[TradeOffScore]
    ranked_order: List[str]
    key_differences: List[str]
    recommendation_summary: str
    
    def to_dict(self) -> Dict:
        return {
            "options": [o.to_dict() for o in self.options],
            "ranked_order": self.ranked_order,
            "key_differences": self.key_differences,
            "recommendation_summary": self.recommendation_summary
        }


class TradeOffAnalyzer:
    """
    Analyzes trade-offs between housing options.
    
    Does NOT:
    - Label areas as safe/dangerous
    - Make predictions
    - Use real crime data
    
    DOES:
    - Compare objective factors
    - Calculate trade-off scores
    - Present balanced recommendations
    """
    
    # Weight configuration
    DEFAULT_WEIGHTS = {
        "cost": 0.30,
        "commute": 0.25,
        "convenience": 0.20,
        "transport": 0.15,
        "amenities": 0.10,
    }
    
    # Budget thresholds (KES)
    BUDGET_THRESHOLDS = {
        "very_affordable": 20000,
        "affordable": 40000,
        "moderate": 60000,
        "expensive": 80000,
        "very_expensive": 100000,
    }
    
    # Commute thresholds (minutes)
    COMMUTE_THRESHOLDS = {
        "very_short": 15,
        "short": 30,
        "moderate": 45,
        "long": 60,
        "very_long": 90,
    }
    
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        user_priorities: Optional[List[Priority]] = None
    ):
        """
        Initialize the analyzer.
        
        Args:
            weights: Custom weights for scoring (must sum to 1.0)
            user_priorities: List of priorities in order of importance
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.priorities = user_priorities or [
            Priority.COST,
            Priority.COMMUTE,
            Priority.TRANSPORT,
            Priority.AMENITIES,
        ]
    
    def analyze_options(
        self,
        options: List[Dict],
        budget_max: float,
        workplace_minutes: int = 30,
    ) -> TradeOffComparison:
        """
        Analyze and compare multiple housing options.
        
        Args:
            options: List of housing options with details
            budget_max: Maximum budget in KES
            workplace_minutes: Target commute time
            
        Returns:
            TradeOffComparison with analysis results
        """
        # Score each option
        scored_options = []
        for option in options:
            score = self._score_option(
                option=option,
                budget_max=budget_max,
                target_commute=workplace_minutes,
            )
            scored_options.append(score)
        
        # Sort by total score
        ranked = sorted(scored_options, key=lambda x: x.total_score, reverse=True)
        ranked_names = [o.option_name for o in ranked]
        
        # Generate key differences
        differences = self._identify_differences(ranked, options)
        
        # Generate summary
        summary = self._generate_summary(ranked, budget_max)
        
        return TradeOffComparison(
            options=scored_options,
            ranked_order=ranked_names,
            key_differences=differences,
            recommendation_summary=summary
        )
    
    def _score_option(
        self,
        option: Dict,
        budget_max: float,
        target_commute: int,
    ) -> TradeOffScore:
        """Score a single housing option."""
        
        # Extract values
        rent = option.get("rent_kes", 50000)
        commute = option.get("commute_minutes", 30)
        transport_score = self._score_transport(option)
        amenities_count = len(option.get("amenities", []))
        
        # Cost score (lower rent = higher score, capped at budget)
        cost_score = self._score_cost(rent, budget_max)
        
        # Commute score (shorter = higher score)
        commute_score = self._score_commute(commute, target_commute)
        
        # Convenience score (amenities + transport combined)
        convenience_score = self._score_convenience(transport_score, amenities_count)
        
        # Priority-specific scores
        priority_scores = {
            "safety_concerns": self._calculate_safety_score(option),
            "cost": cost_score,
            "commute": commute_score,
            "transport": transport_score,
            "amenities": self._score_amenities(amenities_count),
        }
        
        # Calculate weighted total
        total_score = self._calculate_weighted_total(priority_scores)
        
        # Identify strengths
        strengths = self._identify_strengths(option, cost_score, commute_score, transport_score)
        
        # Identify trade-offs
        trade_offs = self._identify_tradeoffs(option, rent, commute, transport_score)
        
        # Generate warnings
        warnings = self._generate_warnings(option, rent, budget_max, commute)
        
        return TradeOffScore(
            option_name=option.get("name", "Unknown"),
            total_score=total_score,
            cost_score=cost_score,
            commute_score=commute_score,
            convenience_score=convenience_score,
            priority_scores=priority_scores,
            strengths=strengths,
            trade_offs=trade_offs,
            warnings=warnings
        )
    
    def _score_cost(self, rent: float, budget_max: float) -> float:
        """Score based on rent vs budget (0-100)."""
        if rent <= 0:
            return 50.0
        
        ratio = rent / budget_max if budget_max > 0 else 1.0
        
        if ratio <= 0.5:
            return 100.0
        elif ratio <= 0.7:
            return 90.0
        elif ratio <= 0.85:
            return 75.0
        elif ratio <= 1.0:
            return 60.0
        else:
            # Over budget - penalty
            return max(0, 60 - (ratio - 1.0) * 50)
    
    def _score_commute(self, commute: int, target: int) -> float:
        """Score based on commute time (0-100, shorter is better)."""
        if commute <= target:
            return 100.0
        elif commute <= target * 1.25:
            return 85.0
        elif commute <= target * 1.5:
            return 70.0
        elif commute <= target * 2:
            return 50.0
        else:
            return max(0, 30 - (commute - target * 2) * 0.5)
    
    def _score_transport(self, option: Dict) -> float:
        """Score based on transport availability (0-100)."""
        transport = option.get("transport_options", [])
        if not isinstance(transport, list):
            transport = [transport]
        
        score = 50  # base score
        
        if "matatu" in [t.lower() for t in transport]:
            score += 20
        if "bodaboda" in [t.lower() for t in transport]:
            score += 15
        if "bus" in [t.lower() for t in transport]:
            score += 15
        if "walking" in [t.lower() for t in transport]:
            score += 10
        if "private" in [t.lower() for t in transport]:
            score += 5
        
        return min(100, score)
    
    def _score_convenience(self, transport_score: float, amenities_count: int) -> float:
        """Score convenience combining transport and amenities."""
        amenities_score = min(50, amenities_count * 10)
        return (transport_score * 0.6 + amenities_score * 0.4)
    
    def _score_amenities(self, count: int) -> float:
        """Score based on number of amenities."""
        return min(100, count * 15)
    
    def _calculate_safety_score(self, option: Dict) -> float:
        """
        Calculate a neutral 'safety' score based on situational factors.
        
        Note: This is about trade-offs, NOT about labeling areas.
        """
        # Base score
        score = 70.0
        
        # Adjust based on objective factors, not stereotypes
        transport = option.get("transport_options", [])
        if "matatu" in [t.lower() for t in transport]:
            score += 5  # More transport options = more flexibility
        
        commute = option.get("commute_minutes", 30)
        if commute > 60:
            score -= 5  # Longer commute = more exposure
        
        # Check for basic infrastructure indicators
        amenities = option.get("amenities", [])
        has_market = any("market" in a.lower() for a in amenities)
        has_health = any("hospital" in a.lower() or "clinic" in a.lower() for a in amenities)
        
        if has_market:
            score += 5  # Local services = more populated area
        if has_health:
            score += 5  # Healthcare access nearby
        
        return max(0, min(100, score))
    
    def _calculate_weighted_total(self, scores: Dict[str, float]) -> float:
        """Calculate weighted total score."""
        total = 0.0
        for category, weight in self.weights.items():
            score = scores.get(category, 50)
            total += score * weight
        return total
    
    def _identify_strengths(
        self,
        option: Dict,
        cost_score: float,
        commute_score: float,
        transport_score: float
    ) -> List[str]:
        """Identify strengths of an option."""
        strengths = []
        name = option.get("name", "This area")
        
        if cost_score >= 90:
            strengths.append(f"{name} offers excellent value within your budget")
        elif cost_score >= 75:
            strengths.append(f"{name} is reasonably priced")
        
        if commute_score >= 90:
            strengths.append(f"Very short commute from {name}")
        elif commute_score >= 75:
            strengths.append(f"{name} has a manageable commute")
        
        if transport_score >= 80:
            strengths.append(f"Multiple transport options available near {name}")
        
        amenities = option.get("amenities", [])
        if len(amenities) >= 4:
            strengths.append(f"Good local amenities (market, shops, services)")
        
        if not strengths:
            strengths.append(f"{name} may suit your specific priorities")
        
        return strengths
    
    def _identify_tradeoffs(
        self,
        option: Dict,
        rent: float,
        commute: int,
        transport_score: float
    ) -> List[str]:
        """Identify trade-offs of an option."""
        tradeoffs = []
        name = option.get("name", "This area")
        
        # Cost vs commute tradeoff
        if rent < 40000 and commute > 45:
            tradeoffs.append(f"Lower rent in {name} but longer commute")
        elif rent > 70000 and commute < 30:
            tradeoffs.append(f"Shorter commute in {name} comes with higher rent")
        
        # Transport tradeoff
        if transport_score < 60:
            tradeoffs.append(f"Limited transport options in {name} - consider availability")
        
        # General tradeoffs
        if rent > 60000:
            tradeoffs.append("Higher rent means less flexibility for other expenses")
        if commute > 60:
            tradeoffs.append("Long commute reduces time for other activities")
        
        if not tradeoffs:
            tradeoffs.append(f"{name} offers balanced trade-offs for your criteria")
        
        return tradeoffs
    
    def _generate_warnings(
        self,
        option: Dict,
        rent: float,
        budget_max: float,
        commute: int
    ) -> List[str]:
        """Generate warnings about an option."""
        warnings = []
        
        if rent > budget_max:
            warnings.append(f"Rent exceeds your stated budget")
        
        if commute > 90:
            warnings.append("Very long commute - consider time and transport costs")
        
        transport = option.get("transport_options", [])
        if not transport or (len(transport) == 1 and "walking" in transport):
            warnings.append("Limited transport options - verify reliability")
        
        return warnings
    
    def _identify_differences(
        self,
        ranked: List[TradeOffScore],
        options: List[Dict]
    ) -> List[str]:
        """Identify key differences between top options."""
        differences = []
        
        if len(ranked) < 2:
            return ["Only one option to compare"]
        
        best = ranked[0]
        second = ranked[1]
        
        # Cost difference
        cost_diff = best.cost_score - second.cost_score
        if abs(cost_diff) > 10:
            winner = "Lower rent option" if cost_diff > 0 else "Higher rent option"
            differences.append(f"Cost: {winner} scores {abs(cost_diff):.0f}% better")
        
        # Commute difference
        commute_diff = best.commute_score - second.commute_score
        if abs(commute_diff) > 10:
            winner = "Shorter commute" if commute_diff > 0 else "Longer commute"
            differences.append(f"Commute: {winner} option scores {abs(commute_diff):.0f}% better")
        
        # Transport difference
        transport_diff = best.priority_scores.get("transport", 0) - second.priority_scores.get("transport", 0)
        if abs(transport_diff) > 15:
            winner = "Better transport" if transport_diff > 0 else "Limited transport"
            differences.append(f"Transport: {winner} option is {abs(transport_diff):.0f}% better")
        
        return differences
    
    def _generate_summary(
        self,
        ranked: List[TradeOffScore],
        budget_max: float
    ) -> str:
        """Generate a summary recommendation."""
        if not ranked:
            return "No options to compare."
        
        best = ranked[0]
        name = best.option_name
        
        summary = f"Based on your criteria and budget of KES {budget_max:,}:\n\n"
        summary += f"**{name}** appears to offer the best balance with:\n"
        
        for strength in best.strengths[:2]:
            summary += f"• {strength}\n"
        
        summary += f"\nKey trade-off: {best.trade_offs[0] if best.trade_offs else 'Balanced across criteria'}\n"
        
        if best.warnings:
            summary += f"\n⚠️  Note: {best.warnings[0]}\n"
        
        summary += "\n*This is advisory information. Visit areas personally and verify current rents.*"
        
        return summary


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("TRADE-OFF ANALYZER TEST")
    print("=" * 80)
    
    analyzer = TradeOffAnalyzer()
    
    # Sample options
    options = [
        {
            "name": "Kileleshwa",
            "rent_kes": 65000,
            "commute_minutes": 25,
            "transport_options": ["matatu", "bus", "private"],
            "amenities": ["market", "hospital", "schools", "shopping"],
        },
        {
            "name": "Ruaka",
            "rent_kes": 35000,
            "commute_minutes": 45,
            "transport_options": ["matatu", "bodaboda"],
            "amenities": ["market", "shops"],
        },
        {
            "name": "Westlands",
            "rent_kes": 80000,
            "commute_minutes": 20,
            "transport_options": ["matatu", "bus", "private"],
            "amenities": ["market", "hospital", "schools", "shopping", "mall"],
        },
    ]
    
    # Analyze
    result = analyzer.analyze_options(
        options=options,
        budget_max=70000,
        workplace_minutes=30,
    )
    
    print(f"\n{'='*40}")
    print("RANKED OPTIONS:")
    print(f"{'='*40}")
    
    for i, option in enumerate(result.options, 1):
        print(f"\n{i}. {option.option_name} (Score: {option.total_score:.1f})")
        print(f"   Cost: {option.cost_score:.0f} | Commute: {option.commute_score:.0f} | Convenience: {option.convenience_score:.0f}")
        print(f"   Strengths: {', '.join(option.strengths[:2])}")
        print(f"   Trade-offs: {option.trade_offs[0]}")
        if option.warnings:
            print(f"   ⚠️  {option.warnings[0]}")
    
    print(f"\n{'='*40}")
    print("KEY DIFFERENCES:")
    print(f"{'='*40}")
    for diff in result.key_differences:
        print(f"• {diff}")
    
    print(f"\n{'='*40}")
    print("RECOMMENDATION:")
    print(f"{'='*40}")
    print(result.recommendation_summary)


"""
Integration test to verify the modular structure works correctly
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.models.housing_models import HousingRequirements, NeighborhoodRecommendation
from src.core.agent_orchestrator import run_housing_agent
from src.utils.chat_utils import interactive_chat


def test_modular_structure():
    """Test that all modules can be imported and basic functionality works"""
    # Test that models can be instantiated
    req = HousingRequirements(
        has_all_details=True,
        target_location="Test City",
        workplace_location="Test Area",
        monthly_budget=15000.0
    )
    
    assert req.target_location == "Test City"
    assert req.monthly_budget == 15000.0
    
    # Test that recommendation model can be instantiated
    rec = NeighborhoodRecommendation(neighborhoods=[])
    assert len(rec.neighborhoods) == 0
    
    print("✓ Models import and instantiate correctly")
    
    # Test that main functions are accessible
    assert callable(run_housing_agent)
    assert callable(interactive_chat)
    
    print("✓ Core functions are accessible")
    
    print("\n🎉 All structural tests passed! Modular architecture is working correctly.")


if __name__ == "__main__":
    test_modular_structure()
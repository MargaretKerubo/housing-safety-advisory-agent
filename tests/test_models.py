"""
Basic tests for the housing safety advisory agent
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import pytest
from src.models.housing_models import HousingRequirements


def test_housing_requirements_model():
    """Test that the HousingRequirements model works correctly"""
    req = HousingRequirements(
        has_all_details=True,
        current_location="Nairobi",
        target_location="Kisumu",
        workplace_location="CBD",
        monthly_budget=20000.0,
        preferences="Secure neighborhood"
    )

    assert req.has_all_details == True
    assert req.target_location == "Kisumu"
    assert req.monthly_budget == 20000.0
    assert "Secure neighborhood" in req.preferences


if __name__ == "__main__":
    test_housing_requirements_model()
    print("All tests passed!")
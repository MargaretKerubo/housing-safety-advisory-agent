"""
Example usage of the skills-based Housing Agent.

Run this script to see how the agent works:
    python examples/agent_example.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.agent_orchestrator import HousingAgent
import json


def example_1_simple_search():
    """Example 1: Simple property search."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Property Search")
    print("="*60)
    
    agent = HousingAgent()
    result = agent.run("Find housing in Kilimani under 30,000 KES per month")
    
    print(f"\nStatus: {result['status']}")
    print(f"Iterations: {result['iterations']}")
    print(f"\nTools Used: {len(result['tool_calls'])}")
    for tc in result['tool_calls']:
        print(f"  - {tc['skill']}: {tc['arguments']}")
    print(f"\nResponse:\n{result['message']}")


def example_2_safety_analysis():
    """Example 2: Deep safety analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Safety Analysis")
    print("="*60)
    
    agent = HousingAgent()
    result = agent.run("Tell me about safety in Westlands - crime rates, lighting, police presence")
    
    print(f"\nStatus: {result['status']}")
    print(f"Tools Used: {[tc['skill'] for tc in result['tool_calls']]}")
    print(f"\nResponse:\n{result['message']}")


def example_3_neighborhood_comparison():
    """Example 3: Compare multiple neighborhoods."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Neighborhood Comparison")
    print("="*60)
    
    agent = HousingAgent()
    result = agent.run(
        "Compare Kilimani, Westlands, and Lavington for safety, affordability, and commute to CBD. "
        "I prioritize safety most, then affordability."
    )
    
    print(f"\nStatus: {result['status']}")
    print(f"Iterations: {result['iterations']}")
    print(f"\nTools Used:")
    for tc in result['tool_calls']:
        print(f"  - {tc['skill']}")
    print(f"\nResponse:\n{result['message']}")


if __name__ == "__main__":
    print("\n🏠 Housing Safety Advisory Agent - Skills-Based Examples")
    print("="*60)
    
    try:
        example_1_simple_search()
        example_2_safety_analysis()
        example_3_neighborhood_comparison()
        
        print("\n" + "="*60)
        print("✅ All examples completed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

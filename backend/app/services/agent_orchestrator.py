from typing import Dict, List, Any, Optional
from app.ai import get_ai_provider
from app.skills import (
    SkillRegistry,
    PropertySearchSkill,
    CrimeStatsSkill,
    TransitDataSkill,
    NeighborhoodComparisonSkill,
    SafetyAnalysisSkill
)
import logging
import json

logger = logging.getLogger(__name__)


class HousingAgent:
    """Orchestrator agent that uses skills to solve housing queries."""
    
    def __init__(self):
        self.ai_provider = get_ai_provider()
        self.skill_registry = SkillRegistry()
        self._register_skills()
        self.max_iterations = 10
    
    def _register_skills(self):
        """Register all available skills."""
        self.skill_registry.register(PropertySearchSkill())
        self.skill_registry.register(CrimeStatsSkill())
        self.skill_registry.register(TransitDataSkill())
        self.skill_registry.register(NeighborhoodComparisonSkill())
        self.skill_registry.register(SafetyAnalysisSkill())
        logger.info(f"Registered {len(self.skill_registry._skills)} skills")
    
    def run(self, user_query: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Run the agent with skill-based orchestration."""
        logger.info(f"🤖 Agent starting: {user_query[:100]}...")
        
        if conversation_history is None:
            conversation_history = []
        
        # System prompt for the agent
        system_prompt = """You are a housing advisory agent helping users find safe, affordable housing in Kenya.

You have access to these tools:
- search_properties: Find rental listings across platforms
- get_crime_stats: Get safety and crime data
- get_transit_data: Get commute information
- compare_neighborhoods: Compare multiple areas
- analyze_safety: Deep dive into safety factors

Your job:
1. Understand what the user needs
2. Use tools to gather real data
3. Provide informed recommendations with reasoning

Be conversational, helpful, and data-driven. Always explain your reasoning."""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_query})
        
        tool_results = []
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"🔄 Iteration {iteration}")
            
            # Get AI response with tool calling
            response = self.ai_provider.generate_with_tools(
                contents=messages,
                tools=self.skill_registry.list_schemas(),
                temperature=0.7
            )
            
            if response["type"] == "text":
                # Agent provided final answer
                logger.info("✅ Agent completed with text response")
                return {
                    "status": "success",
                    "message": response["content"],
                    "tool_calls": tool_results,
                    "iterations": iteration
                }
            
            elif response["type"] == "tool_calls":
                # Execute tool calls
                for tool_call in response["tool_calls"]:
                    skill_name = tool_call["name"]
                    arguments = tool_call["arguments"]
                    
                    logger.info(f"🔧 Executing skill: {skill_name} with {arguments}")
                    
                    result = self.skill_registry.execute(skill_name, **arguments)
                    
                    tool_results.append({
                        "skill": skill_name,
                        "arguments": arguments,
                        "result": result
                    })
                    
                    # Add tool result to conversation
                    messages.append({
                        "role": "assistant",
                        "content": f"Called {skill_name} with {arguments}"
                    })
                    messages.append({
                        "role": "user",
                        "content": f"Tool result: {json.dumps(result)}"
                    })
        
        # Max iterations reached
        logger.warning("⚠️ Max iterations reached")
        return {
            "status": "partial",
            "message": "I gathered some information but need more time to complete the analysis.",
            "tool_calls": tool_results,
            "iterations": iteration
        }

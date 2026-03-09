# How the Skills-Based Housing Agent Works: A Practical Guide

## Table of Contents
1. [Overview](#overview)
2. [Complete Flow Example](#complete-flow-example)
3. [Architecture Breakdown](#architecture-breakdown)
4. [Step-by-Step Execution](#step-by-step-execution)
5. [Code Walkthrough](#code-walkthrough)
6. [Real-World Scenarios](#real-world-scenarios)
7. [Comparison: Old vs New](#comparison-old-vs-new)

---

## Overview

The Housing Safety Advisory Agent now uses **AI-driven orchestration** where the agent dynamically decides which tools (skills) to use based on the user's query.

**Key Concept**: Instead of following a fixed workflow, the AI agent thinks about what information it needs and calls the appropriate tools to gather that data.

---

## Complete Flow Example

Let's trace a real query from start to finish:

### User Query
```
"I need housing in Westlands, Nairobi. My budget is 40,000 KES and I work in CBD. 
Safety is my top priority."
```

### What Happens Behind the Scenes

```
1. User sends query via API
   ↓
2. HousingAgent receives query
   ↓
3. Agent analyzes query with LLM
   ↓
4. LLM decides: "I need property listings and safety data"
   ↓
5. Agent calls search_properties skill
   → Returns: 5 properties in Westlands under 40k
   ↓
6. Agent calls get_crime_stats skill
   → Returns: Crime rate, police presence, lighting info
   ↓
7. Agent calls get_transit_data skill
   → Returns: Commute time from Westlands to CBD
   ↓
8. Agent calls analyze_safety skill
   → Returns: Detailed safety breakdown
   ↓
9. LLM synthesizes all data into recommendation
   ↓
10. Returns final response to user
```

### Response to User
```json
{
  "status": "success",
  "message": "Based on my research, I found 5 properties in Westlands within your 
             40,000 KES budget. Westlands has a safety score of 7.8/10 with low 
             crime rates and good police presence. Your commute to CBD would be 
             20-35 minutes depending on transport mode...",
  "tool_calls": [
    {"skill": "search_properties", "result": {...}},
    {"skill": "get_crime_stats", "result": {...}},
    {"skill": "get_transit_data", "result": {...}},
    {"skill": "analyze_safety", "result": {...}}
  ],
  "iterations": 2
}
```

---

## Architecture Breakdown

### 1. Skills (The Tools)

**Location**: `backend/app/skills/`

Skills are like specialized workers that do specific tasks:

```python
# Example: PropertySearchSkill
class PropertySearchSkill(Skill):
    name = "search_properties"
    description = "Search for rental properties"
    
    def execute(self, neighborhood, max_budget, bedrooms=1):
        # Searches OLX, Airbnb, BuyRentKenya
        # Returns list of properties
        return {"properties": [...]}
```

**Available Skills:**
- `search_properties` - Find rental listings
- `get_crime_stats` - Get safety data
- `get_transit_data` - Get commute info
- `compare_neighborhoods` - Compare multiple areas
- `analyze_safety` - Deep safety analysis

### 2. Skill Registry

**Location**: `backend/app/skills/base.py`

The registry is like a phonebook of available skills:

```python
registry = SkillRegistry()
registry.register(PropertySearchSkill())
registry.register(CrimeStatsSkill())
# ... etc

# Agent can ask: "What skills are available?"
schemas = registry.list_schemas()

# Agent can execute: "Run this skill with these parameters"
result = registry.execute("search_properties", neighborhood="Westlands", max_budget=40000)
```

### 3. Agent Orchestrator

**Location**: `backend/app/services/agent_orchestrator.py`

The orchestrator is the brain that decides what to do:

```python
class HousingAgent:
    def run(self, user_query):
        # 1. Send query + available skills to LLM
        # 2. LLM decides which skills to call
        # 3. Execute those skills
        # 4. Send results back to LLM
        # 5. LLM synthesizes final answer
        # 6. Return to user
```

### 4. AI Providers (Updated)

**Location**: `backend/app/ai/`

AI providers now support **function calling**:

```python
# Old way (just text generation)
response = ai_provider.generate_content(messages)

# New way (with tools)
response = ai_provider.generate_with_tools(
    messages=messages,
    tools=skill_schemas  # LLM can call these
)

# Response can be:
# - Text: "Here's my answer..."
# - Tool calls: "I need to call search_properties with {...}"
```

### 5. API Routes

**Location**: `backend/app/api/agent_routes.py`

New endpoint for skills-based queries:

```python
@agent_bp.route('/query', methods=['POST')
def agent_query():
    data = request.get_json()
    agent = HousingAgent()
    result = agent.run(data['query'])
    return jsonify(result)
```

---

## Step-by-Step Execution

### Iteration 1: Agent Decides What It Needs

**Input to LLM:**
```
System: You are a housing agent. You have these tools:
- search_properties(neighborhood, max_budget, bedrooms)
- get_crime_stats(neighborhood, city)
- get_transit_data(from_location, to_location)
- analyze_safety(neighborhood, city)

User: "Find housing in Westlands under 40k. I work in CBD and need good security."
```

**LLM Response:**
```json
{
  "type": "tool_calls",
  "tool_calls": [
    {
      "name": "search_properties",
      "arguments": {
        "neighborhood": "Westlands",
        "max_budget": 40000,
        "bedrooms": 1
      }
    },
    {
      "name": "get_crime_stats",
      "arguments": {
        "neighborhood": "Westlands",
        "city": "Nairobi"
      }
    }
  ]
}
```

**Agent Action:**
```python
# Execute search_properties
properties = skill_registry.execute("search_properties", 
    neighborhood="Westlands", max_budget=40000, bedrooms=1)

# Execute get_crime_stats
crime_data = skill_registry.execute("get_crime_stats",
    neighborhood="Westlands", city="Nairobi")
```

### Iteration 2: Agent Synthesizes Results

**Input to LLM:**
```
Previous conversation...

Tool Results:
- search_properties returned: {5 properties found, prices 30k-38k}
- get_crime_stats returned: {safety_score: 7.8, crime_rate: "Low", ...}

Now synthesize this into a recommendation for the user.
```

**LLM Response:**
```json
{
  "type": "text",
  "content": "I found 5 properties in Westlands within your budget. 
             Westlands has excellent security with a 7.8/10 safety score..."
}
```

**Agent Returns Final Result**

---

## Code Walkthrough

### 1. User Makes Request

```javascript
// Frontend
fetch('/api/agent/query', {
  method: 'POST',
  body: JSON.stringify({
    query: "Find housing in Westlands under 40k"
  })
})
```

### 2. Flask Route Receives Request

```python
# backend/app/api/agent_routes.py
@agent_bp.route('/query', methods=['POST'])
def agent_query():
    data = request.get_json()
    agent = HousingAgent()
    result = agent.run(data['query'])
    return jsonify(result)
```

### 3. Agent Orchestrator Starts

```python
# backend/app/services/agent_orchestrator.py
class HousingAgent:
    def run(self, user_query):
        # Build conversation
        messages = [
            {"role": "system", "content": "You are a housing agent..."},
            {"role": "user", "content": user_query}
        ]
        
        # Start iteration loop
        iteration = 0
        while iteration < max_iterations:
            # Ask LLM what to do next
            response = self.ai_provider.generate_with_tools(
                contents=messages,
                tools=self.skill_registry.list_schemas()
            )
            
            if response["type"] == "tool_calls":
                # Execute tools
                for tool_call in response["tool_calls"]:
                    result = self.skill_registry.execute(
                        tool_call["name"],
                        **tool_call["arguments"]
                    )
                    # Add result to conversation
                    messages.append({"role": "user", "content": f"Tool result: {result}"})
            
            elif response["type"] == "text":
                # Agent is done, return answer
                return {"status": "success", "message": response["content"]}
```

### 4. AI Provider Calls LLM with Function Calling

```python
# backend/app/ai/openai_provider.py
def generate_with_tools(self, contents, tools, temperature=0.7):
    response = self.client.chat.completions.create(
        model="gpt-4o-mini",
        messages=contents,
        tools=[{"type": "function", "function": tool} for tool in tools],
        temperature=temperature
    )
    
    if response.choices[0].message.tool_calls:
        # LLM wants to call tools
        return {
            "type": "tool_calls",
            "tool_calls": [...]
        }
    else:
        # LLM has final answer
        return {
            "type": "text",
            "content": response.choices[0].message.content
        }
```

### 5. Skills Execute

```python
# backend/app/skills/data_fetching.py
class PropertySearchSkill(Skill):
    def execute(self, neighborhood, max_budget, bedrooms=1):
        # In production: Call real APIs
        # olx_data = requests.get("https://api.olx.co.ke/...")
        # buyrent_data = requests.get("https://buyrentkenya.com/api/...")
        
        # For now: Return mock data
        return {
            "neighborhood": neighborhood,
            "properties": [
                {"title": "2BR Apartment", "price": 35000, "source": "OLX"},
                {"title": "1BR Modern", "price": 30000, "source": "BuyRentKenya"}
            ]
        }
```

---

## Real-World Scenarios

### Scenario 1: Simple Search

**Query**: "Find housing in Kilimani under 30k"

**Agent Flow:**
1. Calls `search_properties(neighborhood="Kilimani", max_budget=30000)`
2. Calls `get_crime_stats(neighborhood="Kilimani", city="Nairobi")`
3. Synthesizes: "Found 3 properties in Kilimani..."

**Tools Used**: 2 skills, 1 iteration

---

### Scenario 2: Complex Comparison

**Query**: "Compare Kilimani, Westlands, and Lavington for safety and commute to CBD"

**Agent Flow:**
1. Calls `compare_neighborhoods(neighborhoods=["Kilimani", "Westlands", "Lavington"], criteria=["safety", "commute"])`
2. Calls `get_transit_data(from="Kilimani", to="CBD")`
3. Calls `get_transit_data(from="Westlands", to="CBD")`
4. Calls `get_transit_data(from="Lavington", to="CBD")`
5. Calls `analyze_safety(neighborhood="Kilimani")`
6. Calls `analyze_safety(neighborhood="Westlands")`
7. Calls `analyze_safety(neighborhood="Lavington")`
8. Synthesizes comprehensive comparison

**Tools Used**: 7 skills, 2-3 iterations

---

### Scenario 3: Exploratory Query

**Query**: "Tell me about safety in Westlands"

**Agent Flow:**
1. Calls `analyze_safety(neighborhood="Westlands", city="Nairobi", focus_areas=["crime", "lighting", "police", "community"])`
2. Synthesizes detailed safety report

**Tools Used**: 1 skill, 1 iteration

---

### Scenario 4: Multi-Turn Conversation

**Turn 1**: "I'm looking for housing in Nairobi"
- Agent: "I can help! What's your budget and where do you work?"

**Turn 2**: "Budget is 40k, I work in Westlands"
- Agent calls `search_properties(neighborhood="Westlands", max_budget=40000)`
- Agent: "Found 5 properties near your workplace..."

**Turn 3**: "What about safety?"
- Agent calls `analyze_safety(neighborhood="Westlands")`
- Agent: "Westlands has excellent safety with..."

---

## Comparison: Old vs New

### Old Approach (Sequential)

```python
# Fixed workflow
def process_housing_request(user_input):
    # Step 1: Always extract requirements
    requirements = triage_requirements(user_input)
    
    # Step 2: Always check if complete
    if not requirements.has_all_details:
        return gather_missing_details(requirements)
    
    # Step 3: Always research neighborhoods
    recommendations = research_neighborhoods(requirements)
    
    # Step 4: Always present
    return present_recommendations(recommendations)
```

**Limitations:**
- ❌ Fixed workflow (can't adapt)
- ❌ No real data (just LLM knowledge)
- ❌ Can't handle exploratory queries
- ❌ Can't compare multiple options
- ❌ No external API integration

---

### New Approach (Skills-Based)

```python
# Dynamic workflow
def run(user_query):
    while not done:
        # Agent decides what to do
        response = llm.decide_next_action(
            query=user_query,
            available_tools=skills,
            previous_results=results
        )
        
        if response.type == "tool_call":
            # Execute the tool agent chose
            result = execute_skill(response.tool_name, response.args)
            results.append(result)
        else:
            # Agent has final answer
            return response.answer
```

**Benefits:**
- ✅ Dynamic (agent decides strategy)
- ✅ Real data (calls external APIs)
- ✅ Handles any query type
- ✅ Can compare, analyze, explore
- ✅ Extensible (add new skills easily)

---

## Key Takeaways

### 1. **Agent Thinks, Then Acts**
The LLM analyzes the query and decides which tools it needs, rather than following a fixed script.

### 2. **Skills Are Modular**
Each skill does one thing well. Add new skills without changing core logic.

### 3. **Real Data Integration**
Skills can call external APIs (Google Maps, property listings, crime databases).

### 4. **Iterative Process**
Agent can call multiple tools, analyze results, and call more tools if needed.

### 5. **Explainable**
You can see exactly which tools were used and what data they returned.

---

## Next Steps for Production

### 1. Replace Mock Data
```python
# In PropertySearchSkill.execute()
olx_response = requests.get("https://api.olx.co.ke/search", 
    params={"location": neighborhood, "max_price": max_budget})
return olx_response.json()
```

### 2. Add API Keys
```bash
# .env
GOOGLE_MAPS_API_KEY=your_key
OLX_API_KEY=your_key
```

### 3. Add More Skills
- `find_nearby_schools`
- `get_hospital_proximity`
- `predict_rent_trends`
- `check_water_electricity_reliability`

### 4. Add Caching
```python
# Cache frequently accessed data
@cache.memoize(timeout=3600)
def get_crime_stats(neighborhood, city):
    # ...
```

### 5. Update Frontend
```javascript
// Use new agent endpoint
const response = await fetch('/api/agent/query', {
  method: 'POST',
  body: JSON.stringify({ query: userInput })
});
```

---

## Testing the Agent

### Start Backend
```bash
cd backend
source venv/bin/activate
python server.py
```

### Test with cURL
```bash
curl -X POST http://localhost:5000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find housing in Westlands under 40k with good security"}'
```

### Run Examples
```bash
cd backend
python ../examples/agent_example.py
```

---

## Summary

**Before**: Fixed workflow → Extract requirements → Research → Present

**Now**: Dynamic orchestration → Agent decides tools → Executes skills → Synthesizes results

The agent is now **intelligent, flexible, and data-driven** rather than following a rigid script.

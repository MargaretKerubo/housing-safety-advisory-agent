# Skills-Based Agent Architecture

## Overview

The Housing Safety Advisory Agent now uses a **skills-based architecture** where an AI orchestrator dynamically selects and executes tools to answer user queries.

## Architecture Components

### 1. Skills (Tools)

Skills are discrete, reusable capabilities that the agent can invoke:

```
app/skills/
├── base.py              # Skill base class and registry
├── data_fetching.py     # External data integration skills
├── analysis.py          # Complex reasoning skills
└── __init__.py
```

#### Available Skills

**Data Fetching Skills:**
- `search_properties`: Search Airbnb, OLX, BuyRentKenya for listings
- `get_crime_stats`: Fetch crime and safety statistics
- `get_transit_data`: Get commute times and transportation options

**Analysis Skills:**
- `compare_neighborhoods`: Multi-criteria comparison with weighted scoring
- `analyze_safety`: Deep dive safety analysis (crime, lighting, police, community)

### 2. Agent Orchestrator

The `HousingAgent` class manages skill execution:

```python
from app.services.agent_orchestrator import HousingAgent

agent = HousingAgent()
result = agent.run("Find safe housing in Kilimani under 30k")
```

**How it works:**
1. User sends query
2. Agent decides which skills to use (via LLM function calling)
3. Skills execute and return data
4. Agent synthesizes results into recommendations
5. Iterates until complete or max iterations reached

### 3. AI Provider Updates

Both OpenAI and Gemini providers now support function calling:

```python
response = ai_provider.generate_with_tools(
    contents=messages,
    tools=skill_schemas,
    temperature=0.7
)
```

## API Endpoints

### New Agent Endpoint

**POST /api/agent/query**

Request:
```json
{
  "query": "Find housing in Westlands with good security under 40k",
  "conversation_history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

Response:
```json
{
  "status": "success",
  "message": "Based on my research...",
  "tool_calls": [
    {
      "skill": "search_properties",
      "arguments": {"neighborhood": "Westlands", "max_budget": 40000},
      "result": {...}
    },
    {
      "skill": "get_crime_stats",
      "arguments": {"neighborhood": "Westlands", "city": "Nairobi"},
      "result": {...}
    }
  ],
  "iterations": 3
}
```

**GET /api/agent/skills**

List all available skills and their schemas.

### Legacy Endpoint (Still Available)

**POST /api/housing-recommendations**

The original sequential workflow endpoint remains for backward compatibility.

## Adding New Skills

1. Create skill class inheriting from `Skill`:

```python
from app.skills.base import Skill
from typing import Dict, Any

class MyNewSkill(Skill):
    @property
    def name(self) -> str:
        return "my_skill_name"
    
    @property
    def description(self) -> str:
        return "What this skill does"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "..."}
            },
            "required": ["param1"]
        }
    
    def execute(self, param1: str) -> Dict[str, Any]:
        # Implementation
        return {"result": "data"}
```

2. Register in `agent_orchestrator.py`:

```python
self.skill_registry.register(MyNewSkill())
```

## Integration with External APIs

### Current Implementation (Mock Data)

Skills currently return mock data. Replace with real API calls:

```python
# In PropertySearchSkill.execute()
# Replace mock data with:
olx_results = requests.get(f"https://api.olx.co.ke/search?location={neighborhood}")
buyrent_results = requests.get(f"https://api.buyrentkenya.com/listings?area={neighborhood}")
```

### Recommended APIs

- **Property Listings**: OLX API, BuyRentKenya API, Airbnb API
- **Crime Data**: Kenya Police API, local crime databases
- **Transit**: Google Maps Directions API, Matatu route APIs
- **Maps**: Google Maps API, OpenStreetMap

### Environment Variables

Add to `.env`:

```bash
# External API Keys
GOOGLE_MAPS_API_KEY=your_key
OLX_API_KEY=your_key
BUYRENTKENYA_API_KEY=your_key
```

## Benefits of Skills-Based Approach

✅ **Dynamic Problem Solving**: Agent decides strategy based on query
✅ **Extensible**: Add new skills without changing core logic
✅ **Real Data Integration**: Connect to external APIs
✅ **Complex Reasoning**: Multi-step analysis with tool chaining
✅ **Explainable**: Track which tools were used and why
✅ **Flexible**: Handles unexpected user requests

## Example Queries

**Simple Query:**
```
"Find housing in Kilimani under 30k"
→ Agent uses: search_properties, get_crime_stats
```

**Complex Query:**
```
"Compare Kilimani, Westlands, and Lavington for safety and commute to CBD"
→ Agent uses: compare_neighborhoods, get_transit_data, analyze_safety (3x)
```

**Exploratory Query:**
```
"Tell me about safety in Kilimani"
→ Agent uses: analyze_safety with all focus areas
```

## Testing

Test the agent:

```bash
curl -X POST http://localhost:5000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find safe housing in Westlands under 40k"}'
```

List available skills:

```bash
curl http://localhost:5000/api/agent/skills
```

## Migration Path

1. ✅ Skills-based architecture implemented
2. ⏳ Replace mock data with real API calls
3. ⏳ Add more skills (price prediction, school proximity, etc.)
4. ⏳ Update frontend to use new agent endpoint
5. ⏳ Deprecate old sequential endpoint

## Performance Considerations

- **Latency**: Multiple LLM calls + API calls (3-10 seconds typical)
- **Cost**: More LLM calls than sequential approach
- **Caching**: Implement Redis for frequently accessed data
- **Rate Limiting**: Respect external API limits

## Next Steps

1. Integrate real APIs (start with Google Maps)
2. Add caching layer
3. Implement error handling and retries
4. Add more skills (schools, hospitals, price trends)
5. Build frontend UI for agent interaction
6. Add conversation memory and context

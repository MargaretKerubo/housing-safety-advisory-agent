# Skills-Based Agent Implementation

## What Changed?

Your Housing Safety Advisory Agent now uses a **skills-based architecture** where an AI orchestrator dynamically selects and executes tools to solve user queries.

## New Structure

```
backend/app/
├── skills/                    # NEW: Skills/Tools system
│   ├── base.py               # Skill base class & registry
│   ├── data_fetching.py      # External API integration skills
│   ├── analysis.py           # Complex reasoning skills
│   └── __init__.py
├── services/
│   ├── housing_service.py    # OLD: Sequential workflow (still works)
│   └── agent_orchestrator.py # NEW: Skills-based orchestrator
├── api/
│   ├── routes.py             # OLD: Original endpoint
│   └── agent_routes.py       # NEW: Agent endpoint
└── ai/
    ├── base.py               # UPDATED: Added function calling
    ├── openai_provider.py    # UPDATED: Function calling support
    └── gemini_provider.py    # UPDATED: Function calling support
```

## Available Skills

### Data Fetching
- **search_properties**: Search Airbnb, OLX, BuyRentKenya
- **get_crime_stats**: Fetch crime and safety data
- **get_transit_data**: Get commute times and transport options

### Analysis
- **compare_neighborhoods**: Multi-criteria comparison with weighted scoring
- **analyze_safety**: Deep dive into safety factors

## New API Endpoints

### POST /api/agent/query
Skills-based agent endpoint with dynamic tool selection.

**Request:**
```json
{
  "query": "Find safe housing in Westlands under 40k",
  "conversation_history": []
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Based on my research...",
  "tool_calls": [
    {"skill": "search_properties", "arguments": {...}, "result": {...}},
    {"skill": "get_crime_stats", "arguments": {...}, "result": {...}}
  ],
  "iterations": 3
}
```

### GET /api/agent/skills
List all available skills.

## Testing

### 1. Start the backend
```bash
cd backend
source venv/bin/activate
python server.py
```

### 2. Test the agent
```bash
# Simple query
curl -X POST http://localhost:5000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find housing in Kilimani under 30k"}'

# List skills
curl http://localhost:5000/api/agent/skills
```

### 3. Run examples
```bash
cd backend
python ../examples/agent_example.py
```

## How It Works

1. **User sends query** → "Find safe housing in Westlands under 40k"
2. **Agent analyzes** → Decides to use `search_properties` and `get_crime_stats`
3. **Skills execute** → Fetch real data from APIs (currently mocked)
4. **Agent synthesizes** → Combines results into recommendations
5. **Returns response** → With reasoning and data sources

## Next Steps

### 1. Replace Mock Data with Real APIs

Edit `backend/app/skills/data_fetching.py`:

```python
def execute(self, neighborhood: str, max_budget: float, bedrooms: int = 1):
    # Replace mock data with:
    olx_response = requests.get(
        f"https://api.olx.co.ke/search",
        params={"location": neighborhood, "max_price": max_budget}
    )
    return olx_response.json()
```

### 2. Add API Keys to .env

```bash
# External APIs
GOOGLE_MAPS_API_KEY=your_key
OLX_API_KEY=your_key
BUYRENTKENYA_API_KEY=your_key
```

### 3. Add More Skills

Create new skills in `backend/app/skills/`:

```python
class SchoolProximitySkill(Skill):
    @property
    def name(self) -> str:
        return "find_nearby_schools"
    
    # ... implement
```

Register in `agent_orchestrator.py`:
```python
self.skill_registry.register(SchoolProximitySkill())
```

### 4. Update Frontend

Point frontend to new endpoint:
```javascript
const response = await fetch('/api/agent/query', {
  method: 'POST',
  body: JSON.stringify({ query: userInput })
});
```

## Benefits

✅ **Dynamic**: Agent decides which tools to use
✅ **Extensible**: Add new skills without changing core logic
✅ **Real Data**: Integrates with external APIs
✅ **Complex Queries**: Handles multi-step reasoning
✅ **Explainable**: Shows which tools were used

## Example Queries

**Simple:**
```
"Find housing in Kilimani under 30k"
→ Uses: search_properties, get_crime_stats
```

**Complex:**
```
"Compare Kilimani, Westlands, and Lavington for safety and commute to CBD"
→ Uses: compare_neighborhoods, get_transit_data, analyze_safety (3x)
```

**Exploratory:**
```
"Tell me about safety in Kilimani"
→ Uses: analyze_safety with all focus areas
```

## Migration

- ✅ Skills-based architecture implemented
- ⏳ Replace mock data with real APIs
- ⏳ Add more skills
- ⏳ Update frontend
- ⏳ Deprecate old endpoint (optional)

## Documentation

See `docs/SKILLS_BASED_ARCHITECTURE.md` for detailed documentation.

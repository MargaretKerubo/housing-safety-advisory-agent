# User Input Specification

## Overview

The Housing Safety Advisory Agent accepts two types of input:

1. **Structured Input**: Direct API calls with defined fields
2. **Natural Language Input**: Free-form text that gets parsed into structured data

This document defines the input shape, required vs optional fields, and example inputs.

---

## Structured Input Shape

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `has_all_details` | boolean | Confirms user has provided sufficient information | `true` |
| `current_location` | string | City/area where user currently lives | `"Kisumu"` |
| `target_location` | string | City/area where user wants to move | `"Nairobi"` |
| `workplace_location` | string | Area near workplace or commute destination | `"Around Prestige Plaza"` |
| `monthly_budget` | number | Maximum monthly rent in KES | `100000.0` |

### Optional Fields (Enhances Recommendations)

| Field | Type | Default | Description | Example |
|-------|------|---------|-------------|---------|
| `preferences` | string | `""` | User's stated preferences | `"Trade-offs between budget and commute"` |
| `risk_tolerance` | enum | `MEDIUM` | LOW / MEDIUM / HIGH risk tolerance | `"medium"` |
| `typical_return_time` | enum | `EVENING` | DAYTIME / EVENING / NIGHT | `"evening"` |
| `living_arrangement` | enum | `ALONE` | ALONE / SHARED / FAMILY | `"alone"` |
| `transport_mode` | enum | `MATATU` | WALKING / BODABODA / MATATU / PRIVATE / BUS | `"matatu"` |
| `commute_minutes` | number | `30` | Expected daily commute time | `30` |
| `familiar_with_area` | boolean | `false` | Has user lived in target area before? | `false` |
| `has_night_activities` | boolean | `false` | Regularly out at night for social/work? | `false` |

### Complete Input Example

```json
{
  "has_all_details": true,
  "current_location": "Kisumu",
  "target_location": "Nairobi",
  "workplace_location": "Around Prestige Plaza",
  "monthly_budget": 100000.0,
  "preferences": "Trade-offs between budget and commute.",
  "risk_tolerance": "medium",
  "typical_return_time": "evening",
  "living_arrangement": "alone",
  "transport_mode": "matatu",
  "commute_minutes": 30,
  "familiar_with_area": false,
  "has_night_activities": false
}
```

---

## Natural Language Input Examples

The agent can parse natural language into structured input. Below are example queries and how they map to the input shape.

### Example 1: Complete Information

**User Query:**
> "I am moving from Kisumu to Nairobi. My budget is 100000 and my new workplace will be around Prestige Plaza. I prefer trade-offs between budget and commute. I am comfortable with moderate risk and usually return home in the evening. I will be living alone and using matatus for transport. My commute is about 30 minutes."

**Parsed Input:**
```json
{
  "has_all_details": true,
  "current_location": "Kisumu",
  "target_location": "Nairobi",
  "workplace_location": "Around Prestige Plaza",
  "monthly_budget": 100000.0,
  "preferences": "Trade-offs between budget and commute.",
  "risk_tolerance": "medium",
  "typical_return_time": "evening",
  "living_arrangement": "alone",
  "transport_mode": "matatu",
  "commute_minutes": 30,
  "familiar_with_area": false,
  "has_night_activities": false
}
```

### Example 2: Safety-Focused Query (Gets Reframed)

**User Query:**
> "I am moving from Kisumu to Nairobi. My budget is 100000 and my workplace is around Prestige Plaza. My preference is safe areas and I have been told Kibera is a very dangerous place."

**Agent Response (Guardrail):**
> "I noticed you mentioned concerns about Kibera. Rather than relying on generalizations, I can help you understand specific factors like commute, budget, and amenities. What factors matter most to you?"

**Parsed Input (After Reframing):**
```json
{
  "has_all_details": true,
  "current_location": "Kisumu",
  "target_location": "Nairobi",
  "workplace_location": "Around Prestige Plaza",
  "monthly_budget": 100000.0,
  "preferences": "Factors to consider - commute, budget, amenities",
  "risk_tolerance": "medium",
  "typical_return_time": "evening",
  "living_arrangement": "alone",
  "transport_mode": "matatu",
  "commute_minutes": 30,
  "familiar_with_area": false,
  "has_night_activities": false
}
```

### Example 3: Low Risk Tolerance

**User Query:**
> "I need to find a place near Westlands. My budget is 80000. I am very concerned about safety - I return home late at night and prefer areas with good security. I will be living with my family."

**Parsed Input:**
```json
{
  "has_all_details": true,
  "current_location": "",
  "target_location": "Nairobi",
  "workplace_location": "Westlands",
  "monthly_budget": 80000.0,
  "preferences": "Safety priority - good security, late night return",
  "risk_tolerance": "low",
  "typical_return_time": "night",
  "living_arrangement": "family",
  "transport_mode": "matatu",
  "commute_minutes": 30,
  "familiar_with_area": false,
  "has_night_activities": true
}
```

### Example 4: Budget-Focused with Walking Preference

**User Query:**
> "Looking for apartments near Karen. My budget is 50000. I don't mind a longer commute if rent is cheaper. I walk to work and prefer quiet areas."

**Parsed Input:**
```json
{
  "has_all_details": true,
  "current_location": "",
  "target_location": "Nairobi",
  "workplace_location": "Karen",
  "monthly_budget": 50000.0,
  "preferences": "Budget priority - longer commute acceptable, walking to work",
  "risk_tolerance": "medium",
  "typical_return_time": "evening",
  "living_arrangement": "alone",
  "transport_mode": "walking",
  "commute_minutes": 60,
  "familiar_with_area": false,
  "has_night_activities": false
}
```

### Example 5: Minimal Information

**User Query:**
> "I need to find a place in Nairobi under 60000."

**Parsed Input (Agent Will Ask Follow-ups):**
```json
{
  "has_all_details": false,
  "current_location": "",
  "target_location": "Nairobi",
  "workplace_location": "",
  "monthly_budget": 60000.0,
  "preferences": "",
  "risk_tolerance": "medium",
  "typical_return_time": "evening",
  "living_arrangement": "alone",
  "transport_mode": "matatu",
  "commute_minutes": 30,
  "familiar_with_area": false,
  "has_night_activities": false
}
```

---

## Input Fields Explained

### Risk Tolerance (`risk_tolerance`)

| Level | Description | Implications |
|-------|-------------|--------------|
| LOW | Prefers shorter commutes, earlier returns, more populated areas | Recommends areas with good lighting, 24h transport |
| MEDIUM | Comfortable with moderate trade-offs | Balanced recommendations |
| HIGH | Longer commutes, later returns acceptable | More flexible options |

### Typical Return Time (`typical_return_time`)

| Value | Description |
|-------|-------------|
| DAYTIME | Before 6 PM |
| EVENING | 6 PM - 9 PM |
| NIGHT | After 9 PM |

### Transport Mode (`transport_mode`)

| Value | Description |
|-------|-------------|
| WALKING | Entire commute on foot |
| BODABODA | Motorcycle taxi |
| MATATU | Public minibus |
| PRIVATE | Personal vehicle |
| BUS | Larger public bus |

### Living Arrangement (`living_arrangement`)

| Value | Description |
|-------|-------------|
| ALONE | Single person household |
| SHARED | Flatmates/roommates |
| FAMILY | Family with dependents |

---

## Guardrail: Stereotypical Input Handling

The agent detects and reframes stereotypical queries:

**Detected Patterns:**
- "Which areas are dangerous?"
- "Is [area] safe to live in?"
- "I heard [area] has high crime"
- "Avoid [area]"

**Reframed Response:**
> "I aim to provide balanced, evidence-based information without relying on stereotypes. Every area has diverse communities with varying experiences. I can help you understand factors to consider and strategies that work for residents in different areas. What specific concerns do you have?"

---

## Input Validation Rules

1. **Minimum Required**: `has_all_details`, `target_location`, `monthly_budget`
2. **Default Fallbacks**: Optional fields use defaults if not provided
3. **Budget Range**: 0 - 999999 KES (reasonable housing budget)
4. **Commute Range**: 0 - 180 minutes

---

## API Usage Examples

### Python
```python
from src.core.agent_orchestrator import run_housing_agent

requirements = {
    "has_all_details": True,
    "current_location": "Kisumu",
    "target_location": "Nairobi",
    "workplace_location": "Westlands",
    "monthly_budget": 100000,
    "preferences": "Balance between cost and commute"
}

result = run_housing_agent(requirements, [])
```

### cURL
```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "has_all_details": true,
    "target_location": "Nairobi",
    "monthly_budget": 100000,
    "workplace_location": "Prestige Plaza"
  }'
```


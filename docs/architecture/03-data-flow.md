# Data Flow

This document shows exactly what data looks like at each stage of a housing recommendation request — from the raw form the user fills in, to the final response displayed on screen.

---

## Overview

```
Form Input (browser)
      │
      ▼
HousingRequest (Pydantic)
      │
      ▼
Formatted user_input string
      │
      ▼
AI Call 1 → HousingRequirements (Pydantic)
      │
      ▼
AI Call 2 → NeighborhoodRecommendation (Pydantic)
      │
      ▼
AI Call 3 → Formatted presentation string
      │
      ▼
Final JSON response (browser)
```

---

## Stage 1 — Form Input

The user fills in the form in `MainApp.js`. The frontend sends this to `POST /api/housing-recommendations`:

```json
{
  "location": "Kisumu",
  "destination": "Kisumu CBD",
  "distance": 1,
  "time": "Evening",
  "budget": 20000,
  "safety": "Medium",
  "arrangement": "Alone",
  "query": "I prefer a quiet area close to public transport"
}
```

---

## Stage 2 — HousingRequest (Pydantic validation)

FastAPI validates the incoming JSON against the `HousingRequest` Pydantic model in `routes_fastapi.py`. If any field is the wrong type, FastAPI rejects the request with a 422 error before any AI work begins.

The validated fields are then assembled into a plain English string that is passed to the AI:

```
I'm looking for housing in Kisumu.
My workplace is in Kisumu CBD.
The commute distance is 1km.
I plan to return at Evening.
My budget is 20000 KES per month.
I prefer Medium safety tolerance.
I will be living Alone.
Additional concerns: I prefer a quiet area close to public transport
```

---

## Stage 3 — AI Call 1 → HousingRequirements

`triage_requirements()` sends the user string to the AI with a system prompt instructing it to extract structured data. The AI returns JSON which is parsed into a `HousingRequirements` object:

```json
{
  "has_all_details": true,
  "current_location": "",
  "target_location": "Kisumu",
  "workplace_location": "Kisumu CBD",
  "monthly_budget": 20000.0,
  "preferences": "Medium safety tolerance; living alone; 1km commute; quiet area near public transport"
}
```

**Branch point:** if `has_all_details` is `false`, the flow stops here and the AI generates a follow-up question asking for the missing fields. The response is returned to the client with `status: needs_more_info`.

---

## Stage 4 — AI Call 2 → NeighborhoodRecommendation

`research_neighborhoods()` sends the `HousingRequirements` data to the AI with a prompt asking for 3–5 neighbourhood recommendations. The AI returns JSON which is parsed into a `NeighborhoodRecommendation` object containing a list of `Neighborhood` objects:

```json
{
  "neighborhoods": [
    {
      "name": "Milimani",
      "distance_to_cbd": "1.5km",
      "average_rent_1br": "15,000 KES",
      "average_rent_2br": "22,000 KES",
      "security_rating": "4/5 stars",
      "security_details": "Gated estates, 24hr guards, well-lit streets, active neighbourhood watch",
      "amenities": ["Nakumatt", "Aga Khan Hospital", "Kisumu Boys High School"],
      "transportation": "Matatus to CBD every 10 minutes, boda bodas available",
      "description": "Upmarket residential area popular with professionals",
      "pros": ["Safe", "Close to CBD", "Good roads"],
      "cons": ["Slightly above budget", "Limited nightlife"]
    }
  ]
}
```

---

## Stage 5 — AI Call 3 → Presentation

`present_recommendations()` sends the full `NeighborhoodRecommendation` JSON back to the AI with a prompt asking it to write a friendly, formatted summary. The AI returns plain text (not JSON):

```
Great news! I've found some excellent neighbourhoods in Kisumu that suit your needs...

## 1. Milimani
📍 1.5km from Kisumu CBD
💰 1BR: 15,000 KES | 2BR: 22,000 KES
🔒 Security: 4/5 stars — Gated estates with 24hr guards...

...

## Next Steps
- Visit each neighbourhood at your intended return time (Evening)
- Ask landlords about security deposit terms
...
```

---

## Stage 6 — Final Response

The complete result is assembled and written to the in-memory task store. The SSE stream picks it up and sends it to the client:

```json
{
  "status": "success",
  "requirements": { ... },
  "recommendations": {
    "neighborhoods": [ ... ]
  },
  "message": "Great news! I've found some excellent neighbourhoods..."
}
```

`MainApp.js` receives this, renders the neighbourhood cards from `recommendations.neighborhoods`, and displays the full text from `message`.

---

## The needs_more_info Branch

If the user submits incomplete information (e.g. no budget), the flow short-circuits after Stage 3:

```json
{
  "status": "needs_more_info",
  "requirements": {
    "has_all_details": false,
    "target_location": "Kisumu",
    "workplace_location": "",
    "monthly_budget": 0
  },
  "message": "I'd love to help you find housing in Kisumu! Could you tell me where you'll be working and what your monthly rent budget is?"
}
```

The frontend displays this message to the user so they can resubmit with the missing details.

---

## Data Models Reference

### HousingRequirements

| Field | Type | Description |
|---|---|---|
| `has_all_details` | bool | Whether enough info exists to proceed |
| `current_location` | str | Where the user is moving from |
| `target_location` | str | City/town they are moving to |
| `workplace_location` | str | Where they will commute to |
| `monthly_budget` | float | Maximum rent in KES |
| `preferences` | str | Any additional preferences |

### Neighborhood

| Field | Type | Description |
|---|---|---|
| `name` | str | Neighbourhood name |
| `distance_to_cbd` | str | Distance to city centre |
| `average_rent_1br` | str | Average 1-bedroom rent in KES |
| `average_rent_2br` | str | Average 2-bedroom rent in KES |
| `security_rating` | str | Rating e.g. "4/5 stars" |
| `security_details` | str | Detailed security description |
| `amenities` | List[str] | Nearby facilities |
| `transportation` | str | Transport options |
| `description` | str | General neighbourhood description |
| `pros` | List[str] | Advantages |
| `cons` | List[str] | Disadvantages |

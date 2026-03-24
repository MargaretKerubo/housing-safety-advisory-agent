# API Reference

Base URL: `http://localhost:5000` (development)

All request and response bodies are JSON. All endpoints are prefixed with `/api`.

---

## POST /api/housing-recommendations

Submits a housing recommendation request. Returns a task ID immediately. The actual AI processing happens in the background.

### Request Body

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `location` | string | Yes | `""` | City or town the user is looking for housing in |
| `destination` | string | No | `""` | Workplace location for commute calculation |
| `distance` | float | No | `1` | Approximate commute distance in km |
| `time` | string | No | `"Day"` | Typical return time: `"Day"`, `"Evening"`, `"Night"` |
| `budget` | integer | No | `20000` | Maximum monthly rent in KES |
| `safety` | string | No | `"Medium"` | Safety priority: `"Low"`, `"Medium"`, `"High"` |
| `arrangement` | string | No | `"Alone"` | Living arrangement: `"Alone"`, `"Shared"`, `"Family"` |
| `query` | string | No | `""` | Any additional concerns or preferences |

### Example Request

```json
{
  "location": "Kisumu",
  "destination": "Kisumu CBD",
  "distance": 1.5,
  "time": "Evening",
  "budget": 20000,
  "safety": "Medium",
  "arrangement": "Alone",
  "query": "I prefer a quiet area near public transport"
}
```

### Response — 200 OK

```json
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "pending"
}
```

| Field | Type | Description |
|---|---|---|
| `task_id` | string | UUID identifying the background task |
| `status` | string | Always `"pending"` on creation |

### Response — 422 Unprocessable Entity

Returned when the request body fails Pydantic validation.

```json
{
  "detail": [
    {
      "loc": ["body", "budget"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

---

## GET /api/tasks/{task_id}/stream

Opens a Server-Sent Events connection that streams task progress until the task completes or fails. This is the primary way the frontend receives updates.

### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `task_id` | string | The UUID returned by `POST /api/housing-recommendations` |

### Response — 200 OK (SSE stream)

The response is a stream of `text/event-stream` messages. Each message is a JSON-serialised task object:

```
data: {"task_id": "f47ac10b...", "status": "processing", "progress": 25, "current_step": "📋 Analyzing requirements...", "result": null, "error": null}

data: {"task_id": "f47ac10b...", "status": "processing", "progress": 50, "current_step": "🔍 Researching neighborhoods...", "result": null, "error": null}

data: {"task_id": "f47ac10b...", "status": "completed", "progress": 100, "current_step": "✅ Complete", "result": {...}, "error": null}
```

**Progress values and their meaning:**

| Progress | Step |
|---|---|
| `10` | 🏠 Starting analysis |
| `25` | 📋 Analyzing requirements |
| `40` | ✅ Requirements complete |
| `50` | 🔍 Researching neighborhoods |
| `75` | 📝 Preparing recommendations |
| `100` | ✅ Complete |

**When `status` is `"completed"`, the `result` field contains:**

```json
{
  "status": "success",
  "requirements": {
    "has_all_details": true,
    "current_location": "",
    "target_location": "Kisumu",
    "workplace_location": "Kisumu CBD",
    "monthly_budget": 20000.0,
    "preferences": "Medium safety; living alone"
  },
  "recommendations": {
    "neighborhoods": [
      {
        "name": "Milimani",
        "distance_to_cbd": "1.5km",
        "average_rent_1br": "15,000 KES",
        "average_rent_2br": "22,000 KES",
        "security_rating": "4/5 stars",
        "security_details": "Gated estates with 24hr security...",
        "amenities": ["Nakumatt", "Aga Khan Hospital"],
        "transportation": "Matatus to CBD every 10 minutes",
        "description": "Upmarket residential area...",
        "pros": ["Safe", "Close to CBD"],
        "cons": ["Slightly above budget"]
      }
    ]
  },
  "message": "Great news! Here are your recommended neighbourhoods in Kisumu..."
}
```

**Or when `status` is `"needs_more_info"`:**

```json
{
  "status": "needs_more_info",
  "requirements": {
    "has_all_details": false,
    "target_location": "Kisumu",
    "workplace_location": "",
    "monthly_budget": 0
  },
  "message": "I'd love to help! Could you tell me where you'll be working and your monthly budget?"
}
```

**When `status` is `"failed"`, the `error` field contains the error message:**

```json
{
  "task_id": "f47ac10b...",
  "status": "failed",
  "progress": 0,
  "current_step": "❌ Error",
  "result": null,
  "error": "Error code: 429 - You exceeded your current quota..."
}
```

### Response — 404 Not Found

```json
{
  "detail": "Task not found"
}
```

---

## GET /api/tasks/{task_id}/status

Returns the current state of a task. Used as a polling fallback when the SSE connection is unavailable.

### Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `task_id` | string | The UUID returned by `POST /api/housing-recommendations` |

### Response — 200 OK

Returns the same task object that is streamed via SSE:

```json
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "processing",
  "progress": 50,
  "current_step": "🔍 Researching neighborhoods...",
  "created_at": "2026-02-24T14:06:00.000000",
  "updated_at": "2026-02-24T14:06:30.000000",
  "result": null,
  "error": null
}
```

### Response — 404 Not Found

```json
{
  "detail": "Task not found"
}
```

---

## GET /api/health

Health check endpoint. Returns immediately with no processing.

### Response — 200 OK

```json
{
  "status": "OK",
  "service": "Housing Safety Advisory Agent"
}
```

---

## Error Handling Summary

| Status Code | Meaning |
|---|---|
| `200` | Success |
| `404` | Task ID not found (expired or never existed) |
| `422` | Request body validation failed |
| `500` | Unhandled server error |

All `500` errors return:

```json
{
  "error": "Failed to generate housing recommendations",
  "message": "<detailed error message>"
}
```

# Sequence Diagrams

This document shows the interaction between every component over time using Mermaid diagrams. These diagrams render automatically in GitHub, GitLab, and most modern documentation tools.

---

## Happy Path — Complete Request

The user submits a form with all required fields. The AI processes it successfully and returns recommendations.

```mermaid
sequenceDiagram
    actor User
    participant Browser as Browser (MainApp.js)
    participant API as FastAPI (routes_fastapi.py)
    participant TM as TaskManager
    participant Thread as Thread Pool
    participant HS as HousingService
    participant AI as AI Provider

    User->>Browser: Fills form and clicks submit
    Browser->>API: POST /api/housing-recommendations
    API->>TM: create_task(user_input)
    TM-->>API: task_id
    API->>Thread: run_in_threadpool(process_housing_task)
    API-->>Browser: { task_id, status: "pending" } ← returns immediately

    Browser->>API: GET /api/tasks/{task_id}/stream (SSE)
    Note over Browser,API: SSE connection stays open

    Thread->>TM: update_task(progress=10, "🏠 Starting...")
    TM-->>Browser: SSE event { progress: 10 }

    Thread->>HS: triage_requirements(user_input)
    Thread->>TM: update_task(progress=25, "📋 Analyzing...")
    TM-->>Browser: SSE event { progress: 25 }
    HS->>AI: generate_content(triage prompt)
    AI-->>HS: JSON string
    HS-->>Thread: HousingRequirements

    Thread->>TM: update_task(progress=40, "✅ Requirements complete")
    TM-->>Browser: SSE event { progress: 40 }

    Thread->>HS: research_neighborhoods(requirements)
    Thread->>TM: update_task(progress=50, "🔍 Researching...")
    TM-->>Browser: SSE event { progress: 50 }
    HS->>AI: generate_content(research prompt)
    AI-->>HS: JSON string
    HS-->>Thread: NeighborhoodRecommendation

    Thread->>HS: present_recommendations(recommendations)
    Thread->>TM: update_task(progress=75, "📝 Preparing...")
    TM-->>Browser: SSE event { progress: 75 }
    HS->>AI: generate_content(presentation prompt)
    AI-->>HS: plain text
    HS-->>Thread: formatted string

    Thread->>TM: update_task(status="completed", progress=100, result={...})
    TM-->>Browser: SSE event { status: "completed", result: {...} }

    Browser->>Browser: Close SSE connection
    Browser->>User: Display neighbourhood cards and recommendations
```

---

## Incomplete Input — needs_more_info Branch

The user submits without all required fields. The flow short-circuits after the first AI call.

```mermaid
sequenceDiagram
    actor User
    participant Browser as Browser (MainApp.js)
    participant API as FastAPI
    participant TM as TaskManager
    participant Thread as Thread Pool
    participant HS as HousingService
    participant AI as AI Provider

    User->>Browser: Submits form (missing budget)
    Browser->>API: POST /api/housing-recommendations
    API->>TM: create_task(user_input)
    API->>Thread: run_in_threadpool(process_housing_task)
    API-->>Browser: { task_id, status: "pending" }

    Browser->>API: GET /api/tasks/{task_id}/stream (SSE)

    Thread->>HS: triage_requirements(user_input)
    HS->>AI: generate_content(triage prompt)
    AI-->>HS: { has_all_details: false, monthly_budget: 0 }
    HS-->>Thread: HousingRequirements(has_all_details=false)

    Thread->>HS: gather_missing_details(requirements)
    HS->>AI: generate_content(follow-up prompt)
    AI-->>HS: "Could you tell me your monthly budget?"
    HS-->>Thread: follow-up string

    Thread->>TM: update_task(status="completed", result={ status: "needs_more_info", message: "..." })
    TM-->>Browser: SSE event { status: "completed", result: { status: "needs_more_info" } }

    Browser->>User: Display follow-up question
```

---

## SSE Failure — Polling Fallback

The SSE connection drops mid-stream. The frontend falls back to polling.

```mermaid
sequenceDiagram
    actor User
    participant Browser as Browser (apiService.js)
    participant API as FastAPI

    Browser->>API: POST /api/housing-recommendations
    API-->>Browser: { task_id }

    Browser->>API: GET /api/tasks/{task_id}/stream (SSE)
    Note over Browser,API: Connection drops after 90s or on error

    Browser->>Browser: SSE error/timeout → fallback to polling

    loop Every 1.5 seconds
        Browser->>API: GET /api/tasks/{task_id}/status
        API-->>Browser: { status: "processing", progress: 50 }
    end

    Browser->>API: GET /api/tasks/{task_id}/status
    API-->>Browser: { status: "completed", result: {...} }
    Browser->>User: Display results
```

---

## Resumable Session — Page Reload Mid-Processing

The user closes the tab while the task is still running, then reopens it.

```mermaid
sequenceDiagram
    actor User
    participant LS as localStorage
    participant Browser as Browser (MainApp.js)
    participant API as FastAPI
    participant TM as TaskManager

    User->>Browser: Submits form
    Browser->>API: POST /api/housing-recommendations
    API-->>Browser: { task_id: "abc-123" }
    Browser->>LS: setItem("current_task_id", "abc-123")

    Note over User,Browser: User closes the tab

    Note over TM: Task continues processing in background thread

    User->>Browser: Reopens the tab
    Browser->>LS: getItem("current_task_id") → "abc-123"
    Browser->>API: GET /api/tasks/abc-123/stream (SSE)
    Note over Browser,API: Reconnects and picks up from current progress
    API-->>Browser: SSE events from current progress onwards

    Browser->>User: Shows progress bar resuming mid-way
```

---

## AI Provider Selection at Startup

How the correct AI provider is chosen when the service is first instantiated.

```mermaid
sequenceDiagram
    participant Route as routes_fastapi.py
    participant HS as HousingAdvisoryService
    participant Factory as factory.py
    participant Config as Config (settings.py)
    participant Env as .env file

    Route->>HS: HousingAdvisoryService()
    HS->>Factory: get_ai_provider()
    Factory->>Config: Config.AI_PROVIDER
    Config->>Env: os.getenv("AI_PROVIDER")
    Env-->>Config: "openai"
    Config-->>Factory: "openai"
    Factory->>Factory: Config.OPENAI_API_KEY
    Factory-->>HS: OpenAIProvider(api_key)
    HS-->>Route: service ready
```

# Introduction to the Housing Safety Advisory Agent

## What Does This Project Do?

The Housing Safety Advisory Agent is a web application that helps people find safe and affordable housing in Kenyan cities. A user fills in a form describing where they want to live, where they work, and what their budget is. The application sends that information to an AI model which reasons over the details and returns a list of recommended neighbourhoods, each with a security rating, rent range, transport options, and a plain-language explanation of the trade-offs.

The goal is to give someone who is relocating — for example from Nairobi to Kisumu — an informed starting point without requiring them to already know the city.

---

## How the Application Is Structured

The project is split into two completely independent parts: a **backend** and a **frontend**. They communicate over HTTP.

```
housing-safety-advisory-agent/
├── backend/        ← Python API server (FastAPI)
├── frontend/       ← React web application
├── docs/           ← All documentation lives here
├── tests/          ← Automated tests
├── .env            ← Environment variables (API keys, config)
└── start_dev.sh    ← Convenience script to start both servers
```

---

## The Backend

The backend is a **FastAPI** application written in Python. It lives entirely inside the `backend/` folder.

```
backend/
├── app/
│   ├── api/        ← HTTP route definitions (what URLs the server exposes)
│   ├── services/   ← Business logic (what the server actually does)
│   ├── ai/         ← AI provider abstraction (Gemini, OpenAI, etc.)
│   ├── schemas/    ← Data models (the shape of requests and responses)
│   └── config/     ← Configuration loaded from the .env file
├── server.py   ← Entry point — run this to start the server
└── requirements.txt    ← Python dependencies
```

### What each folder does

**`api/`** — Defines the HTTP endpoints. When the frontend sends a request to `/api/housing-recommendations`, this is where it lands. The route handler does very little work itself — it immediately hands off to the service layer and returns a task ID to the client.

**`services/`** — Contains the actual logic of the application. There are two services:
- `housing_service.py` — Orchestrates the three-step AI workflow: triage the user's input, research neighbourhoods, then format the final response.
- `task_manager.py` — Manages background tasks using an in-memory store (a Python dictionary). Each task is tracked by a unique ID so the client can poll or stream its progress without waiting on a single long HTTP request.

**`ai/`** — An abstraction layer over AI providers. The rest of the application never calls OpenAI or Gemini directly. It calls a common interface (`AIProvider`) and the correct provider is selected at startup based on the `AI_PROVIDER` environment variable. Adding a new AI provider means adding one file here without touching anything else.

**`schemas/`** — Pydantic models that define the shape of data flowing through the system. The key models are `HousingRequirements` (what the user needs), `Neighborhood` (a single recommendation), and `NeighborhoodRecommendation` (a list of them).

**`config/`** — A single `Config` class that reads all environment variables from the `.env` file. Every other module reads configuration from here rather than calling `os.getenv` directly.

---

## The Frontend

The frontend is a **React** application. It lives entirely inside the `frontend/` folder.

```
frontend/
├── src/
│   ├── components/     ← React components (the visible pages)
│   │   ├── AuthFlow.js     ← Login / registration screen
│   │   └── MainApp.js      ← Main form and results display
│   ├── utils/
│   │   ├── apiService.js       ← General HTTP client
│   │   └── housingTaskClient.js ← SSE client for streaming task progress
│   └── styles/         ← CSS files
└── package.json
```

The user interacts with `MainApp.js`. When they submit the form, `housingTaskClient.js` sends the request to the backend, receives a task ID immediately, then opens a Server-Sent Events (SSE) connection to stream live progress updates ("Analysing requirements... Researching neighbourhoods...") until the result is ready.

---

## How a Request Flows Through the System

```
User fills form
      │
      ▼
MainApp.js (React)
      │  POST /api/housing-recommendations
      ▼
routes_fastapi.py
      │  Creates a task in memory, returns task_id immediately
      │  Starts background thread
      ▼
housing_service.py (runs in thread pool — does not block the server)
      │
      ├── Step 1: triage_requirements()   → AI call → HousingRequirements
      ├── Step 2: research_neighborhoods() → AI call → NeighborhoodRecommendation
      └── Step 3: present_recommendations() → AI call → formatted text
      │
      ▼
task_manager.py (writes progress to in-memory store at each step)
      │
      ▼
housingTaskClient.js (reads SSE stream from /api/tasks/{task_id}/stream)
      │
      ▼
MainApp.js displays progress bar → then displays results
```

---

## Key Design Decisions

**Non-blocking requests** — AI calls take 30–60 seconds. The server returns a task ID in under 100ms and processes the work in a background thread. The client streams progress via SSE rather than waiting on a single long HTTP request.

**Resumable sessions** — The task ID is stored in the browser's `localStorage`. If the user closes the tab and reopens it, the frontend detects the stored task ID and reconnects to the SSE stream to pick up where it left off. Note: because tasks are held in memory, they are lost if the server restarts.

**AI provider abstraction** — The application is not tied to any single AI provider. Switching from OpenAI to Gemini (or any future provider) requires only changing one line in the `.env` file.

---

## Running the Project

```bash
# 1. Copy and fill in environment variables
cp .env.example .env

# 2. Start the backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 server.py

# 3. Start the frontend (in a separate terminal)
cd frontend
npm install && npm start
```

Or run both at once from the project root:

```bash
./start_dev.sh
```

Backend runs on `http://localhost:5000`  
Frontend runs on `http://localhost:3000`

---

## Where to Go Next

| Topic | Document |
|---|---|
| AI provider abstraction in detail | `docs/architecture/01-ai-provider-abstraction.md` |
| FastAPI, background tasks and SSE | `docs/architecture/02-fastapi-background-tasks-sse.md` |
| Data flow and payload shapes | `docs/architecture/03-data-flow.md` |
| Sequence diagrams | `docs/architecture/04-sequence-diagrams.md` |
| API reference | `docs/architecture/05-api-reference.md` |
| Environment configuration | `docs/architecture/06-environment-configuration.md` |
| Backend setup | `backend/README.md` |

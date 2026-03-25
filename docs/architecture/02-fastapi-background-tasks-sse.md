# FastAPI, Background Tasks, and Server-Sent Events

## Why We Moved Away From Flask

The original backend was a Flask application. Flask is synchronous — when a request comes in, the server handles it from start to finish before it can handle the next one. For most web applications this is fine. For this one it was a problem.

Every housing recommendation requires three AI calls in sequence. Each call takes between 10 and 30 seconds. That means a single request ties up the server for up to 60–90 seconds. During that time:

- The client sits idle waiting for a response
- Any other requests queue up behind it
- The browser eventually gives up and shows a timeout error

FastAPI solves this because it is built on an **async event loop** (via `uvicorn` and `asyncio`). The server can handle many requests concurrently without any of them blocking the others.

---

## The Problem With Async and Synchronous AI SDKs

FastAPI being async does not automatically make everything fast. The OpenAI and Gemini SDKs make regular blocking HTTP calls — they are synchronous. If you call them directly inside an `async` route handler, you block the entire event loop, which is worse than Flask because it freezes every concurrent request at once.


```
Without run_in_threadpool:
  Event loop → async route → AI call (blocks for 60s) → event loop frozen
  Every other request is stuck waiting
```

The solution is `run_in_threadpool`. It offloads a synchronous function to a separate thread so the event loop stays free.

```
With run_in_threadpool:
  Event loop → async route → thread pool → AI call (60s in separate thread)
  Event loop stays free, handles SSE streams and new requests normally
```

This is why `process_housing_task` is a plain `def` (synchronous), not `async def`. It is designed to run in a thread, not on the event loop.

---

## How a Request Is Handled

### Step 1 — Client submits the form

`POST /api/housing-recommendations` arrives at `routes_fastapi.py`. The route handler is `async`:

```python
@router.post("/housing-recommendations", response_model=TaskResponse)
async def create_housing_recommendation(request: HousingRequest, background_tasks: BackgroundTasks):
```

### Step 2 — Task is created and response is returned immediately

A unique task ID is generated and the task is stored in memory with `status: pending`. The route returns the task ID to the client in under 100ms — before any AI work has started.

```python
task_id = task_manager.create_task(user_input)
background_tasks.add_task(run_in_threadpool, process_housing_task, task_id, user_input)
return TaskResponse(task_id=task_id, status="pending")
```

### Step 3 — AI work runs in the background

`process_housing_task` runs in a thread pool. It calls the housing service step by step, updating the task's progress in memory after each step:

```
progress=10   Starting analysis
progress=25   Analyzing requirements
progress=40   Requirements complete
progress=50   Researching neighborhoods
progress=75   Preparing recommendations
progress=100  Complete
```

### Step 4 — Client streams progress via SSE

As soon as the client receives the task ID, it opens a Server-Sent Events connection to `/api/tasks/{task_id}/stream`. The server streams progress updates every 500ms until the task completes.

```python
@router.get("/tasks/{task_id}/stream")
async def stream_task_progress(task_id: str):
    async def event_generator():
        last_progress = -1
        while True:
            task = task_manager.get_task(task_id)
            if task["progress"] != last_progress:
                yield f"data: {json.dumps(task)}\n\n"
                last_progress = task["progress"]
            if task["status"] in ["completed", "failed"]:
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

---

## What Are Server-Sent Events?

Server-Sent Events (SSE) is a standard browser API for receiving a stream of updates from a server over a single HTTP connection. The server keeps the connection open and pushes new data whenever it has something to say. The client listens passively.

SSE was chosen over WebSockets because:

- **Simpler** — SSE is one-directional (server → client). WebSockets are bidirectional. We only need one direction here.
- **No extra library** — SSE works natively in every modern browser with `EventSource`.
- **HTTP-native** — SSE works over standard HTTP/1.1. It passes through proxies and load balancers without special configuration.

Each SSE message is a JSON-serialised task object:

```json
{
  "task_id": "abc-123",
  "status": "processing",
  "progress": 50,
  "current_step": "Researching neighborhoods...",
  "result": null,
  "error": null
}
```

When `status` becomes `completed`, the `result` field contains the full recommendations. The client closes the connection.

---

## Polling Fallback

If the SSE connection fails (network interruption, proxy timeout), the frontend falls back to polling `/api/tasks/{task_id}/status` every second. This endpoint returns the same task object from the in-memory store.

```python
@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

---

## Resumable Sessions

The task ID is stored in the browser's `localStorage` as soon as it is received. If the user closes the tab mid-processing and reopens it, `housingTaskClient.js` detects the stored task ID on load and reconnects to the SSE stream automatically.

```javascript
if (client.hasResumableTask()) {
    client.resumeTask(onProgress, onComplete, onError);
}
```

**Limitation:** tasks are held in the server's memory. If the server restarts while a task is in progress, the task is lost and the client will receive a 404 when it tries to reconnect. A potential future solution is to use redis to store such running tasks as opposed to saving them in an inmemory map.

---

## The Task Manager

`task_manager.py` is a thin wrapper around a module-level Python dictionary. There is no database or external service involved.

```python
_tasks: Dict[str, Dict[str, Any]] = {}
```

It exposes three methods:

- `create_task(user_input)` — generates a UUID, stores the initial task state, returns the ID
- `get_task(task_id)` — returns the task dict or `None`
- `update_task(task_id, ...)` — updates any combination of `status`, `progress`, `current_step`, `result`, `error`

---

## Application Entry Point

`server_fastapi.py` starts the server using `uvicorn`, which is the ASGI server that runs the FastAPI application:

```python
uvicorn.run(
    "app.main:app",
    host=Config.HOST,
    port=Config.PORT,
    reload=Config.DEBUG
)
```

`app.main` refers to the `app` object created in `backend/app/main.py`, which registers the router, CORS middleware, and optionally serves the built React frontend as static files.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/housing-recommendations` | Submit a request, returns `task_id` immediately |
| `GET` | `/api/tasks/{task_id}/stream` | SSE stream of task progress |
| `GET` | `/api/tasks/{task_id}/status` | Polling fallback — returns current task state |
| `GET` | `/api/health` | Health check |

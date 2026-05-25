# Backend Issues & Improvements — To-Do List

> Work through these one by one. Each issue has a clear description of the problem,
> why it matters, and exactly what needs to be done to fix it.

---

## ISSUE 1 — No Guardrails / Ethical Filter
**Priority:** High
**Status:** [x] Completed

### Problem
The project's own design guide says the agent must refuse biased or harmful queries
like *"Which areas are dangerous?"* and reframe them politely. This logic does not
exist anywhere in the code. Any input — no matter how biased or harmful — goes
straight to the AI unchecked.

### Why It Matters
Without guardrails, the agent can be used to stigmatize neighborhoods, produce
biased recommendations, or be manipulated into giving harmful advice. This directly
violates the project's ethical design principles and its SDG 11 alignment.

### What To Do
- [ ] Create a new file: `backend/app/services/guardrails.py`
- [ ] Write a function that checks the user's input before it reaches the AI
- [ ] Define a list of patterns/keywords that should be refused or reframed
- [ ] If the input is problematic, return a reframed response instead of proceeding
- [ ] Call this function at the very start of `process_housing_request()` in `housing_service.py`

### Example Behaviour
```
User asks:  "Which neighborhoods are dangerous and full of criminals?"
Agent says: "I can't rank areas by danger, but I can help you compare
             housing options based on commute safety, lighting, and
             transport availability. Would you like to try that instead?"
```

---

## ISSUE 2 — No Conversation Memory
**Priority:** High
**Status:** [x] Completed

### Problem
Every request starts completely fresh. The `conversation_history` parameter exists
in `process_housing_request()` but `routes.py` never passes any history into it.
The agent has no memory of what the user said in previous messages.

### Why It Matters
A real AI agent should remember the conversation. If a user says "I want to move
to Kisumu" and then follows up with "actually make it Nairobi", the agent currently
has no idea what "actually" refers to. Every message is treated as if it is the
first one ever sent.

### What To Do
- [ ] Add a session ID system to `routes.py` — each user gets a unique session ID
- [ ] Store conversation history per session (a simple in-memory dictionary is fine to start)
- [ ] On each new request, retrieve the existing history for that session
- [ ] Pass the history into `process_housing_request()` so the AI has full context
- [ ] Append each new user message and AI response to the session history
- [ ] Set a maximum history length (e.g. last 10 messages) to avoid unbounded growth

---

## ISSUE 3 — No Token Limits on AI Calls (Unbounded Consumption)
**Priority:** High
**Status:** [x] Completed

### Problem
Every AI call in `housing_service.py` (lines 48, 83, 138, 180) and
`gemini_provider.py` (line 30) has no `max_tokens` limit. The AI can return
responses of any length, consuming unlimited API credits and slowing down
or crashing the system.

### Why It Matters
Without token limits, a single malicious or accidental request could generate
an enormous AI response, resulting in huge unexpected API bills or a denial
of service where the server becomes too slow to respond to other users.

### What To Do
- [ ] Add a `max_tokens` parameter to the `generate_content()` method signature in `base.py`
- [ ] Pass appropriate token limits in each call inside `housing_service.py`:
  - Triage call (Step 1): max 300 tokens — it only needs to extract a few fields
  - Research call (Step 2): max 2000 tokens — needs detail for 3-5 neighborhoods
  - Presentation call (Step 3): max 1500 tokens — a readable summary
  - Missing details call: max 150 tokens — just a short follow-up question
- [ ] Implement the `max_tokens` limit in both `gemini_provider.py` and `openai_provider.py`
- [ ] Add input length validation in `routes.py` — reject requests where any single
      field exceeds a reasonable character limit (e.g. 500 characters for the query field)

---

## ISSUE 4 — No Rule-Based Risk Engine
**Priority:** High
**Status:** [x] Completed

### Problem
The project design guide explicitly states:
> *"Rule-Based Risk Evaluation Engine — This component must not use AI."*

Right now the AI decides everything — including risk levels. There are no
deterministic rules in the code at all. The same inputs could produce different
risk assessments on different runs because the AI is non-deterministic.

### Why It Matters
The project's core promise is **explainability** — every recommendation must be
traceable to clear rules and inputs. If the AI is making the risk decisions, you
cannot explain *why* a neighborhood was rated a certain way. The agent becomes
a black box, which defeats its entire purpose.

### What To Do
- [ ] Create a new file: `backend/app/services/risk_engine.py`
- [ ] Implement deterministic rules that take the user's inputs and produce a risk score:
  - If `time_of_day = night` AND `commute_distance > 5km` → raise risk level
  - If `living_arrangement = alone` AND `time_of_day = night` → raise risk level
  - If `safety_tolerance = low` → apply stricter neighborhood filters
  - If `budget` is very low → flag that high-security areas may be unaffordable
- [ ] Output a structured risk profile: `{ level: "Medium", factors: [...], score: 6 }`
- [ ] Pass this risk profile into `research_neighborhoods()` so the AI uses it
      to explain recommendations — but the AI does NOT decide the risk level itself
- [ ] Pass the risk profile into `present_recommendations()` so the final message
      explains the reasoning in terms of the rules that were applied

---

## ISSUE 5 — Path Traversal Security Vulnerability
**Priority:** High
**Status:** [x] Completed

### Problem
In `app/main.py` lines 33–34, user-controlled input is used to construct file
paths without any sanitisation. An attacker could send a request with a path
like `../../secret_file` to access files outside the intended directory.

### Why It Matters
This is a well-known security vulnerability (CWE-22). It could allow an attacker
to read sensitive files on the server — including the `.env` file containing
your API keys.

### What To Do
- [ ] Open `app/main.py` and find the file path construction at lines 33–34
- [ ] Replace the unsafe path construction with Flask's `safe_join()`:
  ```python
  from flask import safe_join
  safe_path = safe_join(app.static_folder, path)
  ```
- [ ] Add a check that the resolved path starts with the expected base directory
      before serving the file
- [ ] Never use raw user input directly in `os.path.join()` or similar functions

---

## ISSUE 6 — No Retry Logic on AI Failures
**Priority:** Medium
**Status:** [x] Completed

### Problem
If any AI call fails — due to a rate limit, timeout, or network error — the entire
request immediately crashes with a 500 error. There is no retry, no fallback,
and no graceful degradation. The user sees a generic error with no explanation.

### Why It Matters
AI APIs fail regularly in production — rate limits are hit, networks hiccup,
services go down briefly. Without retry logic, every one of these temporary
failures becomes a visible error for the user, making the app feel unreliable.

### What To Do
- [ ] Create a retry wrapper function in `backend/app/ai/base.py` or a new
      `backend/app/utils/retry.py` file
- [ ] Wrap every `generate_content()` call with retry logic:
  - Retry up to 3 times
  - Wait 1 second before the first retry, 2 seconds before the second (exponential backoff)
  - Only retry on network errors or rate limit errors, not on bad input errors
- [ ] If all retries fail, return a clear, user-friendly error message:
      *"We're having trouble reaching the AI right now. Please try again in a moment."*
- [ ] Log every retry attempt so the team can monitor how often failures occur

---

## ISSUE 7 — Service Re-Instantiated on Every Request
**Priority:** Medium
**Status:** [x] Completed

### Problem
In `routes.py`, `HousingAdvisoryService()` is created fresh on every single
incoming request. This means a new AI provider client (with its connection setup)
is initialised on every call — wasteful and slower than necessary.

### Why It Matters
Under any real load — multiple users using the app at the same time — this
creates unnecessary overhead. The AI client should be set up once and reused,
not rebuilt from scratch for every request.

### What To Do
- [ ] Move the `HousingAdvisoryService()` instantiation out of the route function
- [ ] Instantiate it once when the app starts up, either:
  - As a module-level variable in `routes.py`, or
  - Using Flask's application context so it is shared across requests
- [ ] Make sure the service is stateless between requests (it should be — verify
      that no user-specific data is stored on the service instance itself)

---

## ISSUE 8 — Task Manager Is Disconnected (No Progress Feedback)
**Priority:** Medium
**Status:** [x] Completed

### Problem
`task_manager.py` is fully built but never used anywhere. The 3-step AI pipeline
has no progress reporting. Users submit a request and then wait 5–15 seconds
with no feedback — no indication that anything is happening.

### Why It Matters
A blank waiting screen is a poor user experience. Users do not know if the app
is working, stuck, or crashed. Progress feedback makes the app feel responsive
and trustworthy.

### What To Do
- [ ] Wire `TaskManager` into `housing_service.py`:
  - Create a task at the start of `process_housing_request()`
  - Update progress to 33% after Step 1 completes
  - Update progress to 66% after Step 2 completes
  - Update progress to 100% after Step 3 completes
- [ ] Add a new endpoint in `routes.py`: `GET /api/tasks/<task_id>`
      that returns the current status and progress of a task
- [ ] Update the main `POST /api/housing-recommendations` endpoint to return
      a `task_id` immediately, so the frontend can start polling for progress
- [ ] Update the frontend to poll `GET /api/tasks/<task_id>` every second
      and display a progress bar while waiting

---

## ISSUE 9 — Naive Datetime in `task_manager.py`
**Priority:** Low
**Status:** [x] Completed

### Problem
`task_manager.py` uses `datetime.utcnow()` at lines 16–17 and 49–50.
This returns a timezone-unaware datetime object, which can cause subtle bugs
when comparing timestamps or displaying times to users in different time zones.

### Why It Matters
Python's own documentation discourages `utcnow()` because the returned object
has no timezone information attached to it. This can cause incorrect time
comparisons and confusing behaviour when the app is deployed on a server in
a different timezone to the users.

### What To Do
- [ ] Open `backend/app/services/task_manager.py`
- [ ] Replace every instance of `datetime.utcnow()` with `datetime.now(timezone.utc)`
- [ ] Add `timezone` to the import at the top of the file:
  ```python
  from datetime import datetime, timezone
  ```
- [ ] This is a small change but removes a class of subtle time-related bugs

---

## Progress Tracker

| # | Issue | Priority | Status |
|---|---|---|---|---|
| 1 | No guardrails / ethical filter | High | [x] Completed |
| 2 | No conversation memory | High | [x] Completed |
| 3 | No token limits on AI calls | High | [x] Completed |
| 4 | No rule-based risk engine | High | [x] Completed |
| 5 | Path traversal security vulnerability | High | [x] Completed |
| 6 | No retry logic on AI failures | Medium | [x] Completed |
| 7 | Service re-instantiated on every request | Medium | [x] Completed |
| 8 | Task manager disconnected | Medium | [x] Completed |
| 9 | Naive datetime in task_manager.py | Low | [x] Completed |

# Frontend Integration — Housing Safety Advisory Agent

This document shows sample `curl` commands to test the simple Python HTTP server and explains the included HTML form.

Prerequisite: start the server from the project root:

```bash
python3 simple_server.py
```

Endpoints
- `GET /` — Serves the test HTML form at `docs/form.html`.
- `POST /submit` — Accepts JSON or form-urlencoded payloads and returns the agent response as JSON.

Payload options
- Free-text: provide a single `user_input` string. The server forwards it directly to the agent.
- Structured: provide `current_location`, `target_location`, `workplace_location`, `monthly_budget`, and `preferences`. The server will build a prompt from these fields.

Example curl commands

- Free-text (single prompt):

```bash
curl -s -X POST http://localhost:8000/submit \
  -H "Content-Type: application/json" \
  -d '{"user_input":"I am moving from Nairobi to Kisumu, working in Kisumu CBD, budget 15000 KES."}'
```

- Structured JSON:

```bash
curl -s -X POST http://localhost:8000/submit \
  -H "Content-Type: application/json" \
  -d '{"current_location":"Nairobi","target_location":"Kisumu","workplace_location":"Kisumu CBD","monthly_budget":15000,"preferences":"near public transport"}'
```

- Form-urlencoded (useful to simulate browser form submission):

```bash
curl -s -X POST http://localhost:8000/submit \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode 'target_location=Kisumu' \
  --data-urlencode 'workplace_location=Kisumu CBD' \
  --data-urlencode 'monthly_budget=15000'
```

Response

The server responds with a JSON object returned from the agent. Typical structure (example):

```json
{
  "status": "success",
  "requirements": { ... },
  "recommendations": { ... },
  "message": "..."
}
```

Notes
- The test HTML form is at `docs/form.html`. Open `http://localhost:8000/` to use it — it sends JSON to `/submit` and displays the JSON response.
- The API calls `run_housing_agent()` which may require external credentials (for the GenAI client). Ensure any required environment variables are set before using the server in a real environment.

Troubleshooting
- If you get import errors when running the server, run from the project root so `src/` is importable, e.g. `python3 simple_server.py` from the repository root.
- If the agent fails due to missing external services, the server will return a JSON error with `status: "error"` and an error `message`.

If you'd like, I can also:
- Add CORS headers to `simple_server.py` so a remote frontend can call it from a browser, or
- Create a tiny JavaScript client snippet for direct frontend integration.

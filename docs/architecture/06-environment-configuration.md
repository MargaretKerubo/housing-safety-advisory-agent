# Environment Configuration

All configuration is managed through a single `.env` file in the project root. The backend reads it via the `Config` class in `backend/app/config/settings.py`. No other file calls `os.getenv` directly.

---

## File Location

```
housing-safety-advisory-agent/
├── .env              ← your local config (never commit this)
├── backend/
│   └── .env.example  ← template to copy from
```

To get started:

```bash
cp backend/.env.example .env
```

---

## All Variables

### AI Provider

| Variable | Required | Default | Description |
|---|---|---|---|
| `AI_PROVIDER` | No | `gemini` | Which AI provider to use. Accepted values: `openai`, `gemini` |
| `OPENAI_API_KEY` | If `AI_PROVIDER=openai` | — | Your OpenAI API key |
| `GEMINI_API_KEY` | If `AI_PROVIDER=gemini` | — | Your Google Gemini API key |

**Switching providers** requires only changing `AI_PROVIDER` and ensuring the corresponding key is set. No code changes needed.

```bash
# Use OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...

# Use Gemini
AI_PROVIDER=gemini
GEMINI_API_KEY=AIza...
```

If the key for the selected provider is missing, the server will raise a `ValueError` on startup:
```
ValueError: OPENAI_API_KEY not found in environment
```

---

### Server

| Variable | Required | Default | Description |
|---|---|---|---|
| `HOST` | No | `0.0.0.0` | Host address the server binds to |
| `PORT` | No | `5000` | Port the server listens on |
| `DEBUG` | No | `False` | Enables auto-reload and verbose error pages. Set to `True` in development only |

```bash
HOST=0.0.0.0
PORT=5000
DEBUG=True
```

---

### Frontend

| Variable | Required | Default | Description |
|---|---|---|---|
| `FRONTEND_BUILD_PATH` | No | `../frontend/build` | Path to the built React app. Only needed if serving the frontend from the backend in production |

In development the frontend runs on its own dev server (`npm start`) so this variable is not needed.

---

### Frontend Environment Variables

The React frontend has its own environment variable, set in `frontend/.env` (not the root `.env`):

| Variable | Required | Default | Description |
|---|---|---|---|
| `REACT_APP_API_BASE_URL` | No | `http://localhost:5000` | The backend URL the frontend sends requests to |

```bash
# frontend/.env
REACT_APP_API_BASE_URL=http://localhost:5000
```

Note: React environment variables must be prefixed with `REACT_APP_` to be accessible in the browser.

---

## Complete Example

```bash
# ── AI Provider ──────────────────────────────
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-key-here
GEMINI_API_KEY=AIzaSy-your-key-here

# ── Server ───────────────────────────────────
HOST=0.0.0.0
PORT=5000
DEBUG=False
```

---

## What Breaks If a Variable Is Missing

| Missing Variable | What Happens |
|---|---|
| `AI_PROVIDER` | Defaults to `gemini` |
| `OPENAI_API_KEY` (when `AI_PROVIDER=openai`) | `ValueError` on first request — server starts but crashes when a task is created |
| `GEMINI_API_KEY` (when `AI_PROVIDER=gemini`) | Same as above |
| `PORT` | Server starts on port `5000` |
| `DEBUG` | Defaults to `False` — no auto-reload |
| `REACT_APP_API_BASE_URL` | Frontend defaults to `http://localhost:5000` |

---

## Security Notes

- **Never commit `.env` to version control.** It is listed in `.gitignore`.
- **Never log API keys.** The `Config` class stores them as class attributes but they are never printed or logged anywhere in the codebase.
- The `.env.example` file contains only placeholder values and is safe to commit.

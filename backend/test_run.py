import sys
sys.stdout.reconfigure(line_buffering=True)

from app import create_app
from app.services.risk_engine import evaluate_risk
from app.services.guardrails import check_input

app = create_app()
client = app.test_client()

print("=" * 60)
print("TEST 1 — Health check endpoint")
print("=" * 60)
r = client.get('/api/health')
print("Status:", r.status_code)
print("Response:", r.get_json())

print()
print("=" * 60)
print("TEST 2 — Issue 1: Guardrail blocks biased query")
print("=" * 60)
cases = [
    "Which are the most dangerous areas to avoid?",
    "Rank neighborhoods by crime rate",
    "I want to move to Kisumu, budget 15000 KES",
    "",
    "x" * 2001,
]
for query in cases:
    result = check_input(query)
    preview = query[:60] + "..." if len(query) > 60 else query
    print(f"Input: '{preview}'")
    print(f"  allowed={result['allowed']}", end="")
    if not result["allowed"]:
        print(f" | message: {result['message'][:80]}...")
    else:
        print()

print()
print("=" * 60)
print("TEST 3 — Issue 3: Input field length validation in route")
print("=" * 60)
r = client.post('/api/housing-recommendations', json={
    'location': 'Nairobi',
    'destination': 'CBD',
    'distance': 5,
    'time': 'Day',
    'budget': 15000,
    'safety': 'Medium',
    'arrangement': 'Alone',
    'query': 'x' * 600,
    'session_id': 'test-length'
})
print("Status:", r.status_code)
data = r.get_json()
print("Result status:", data.get('status'))
print("Message:", data.get('message'))

print()
print("=" * 60)
print("TEST 4 — Issue 4: Risk engine deterministic scoring")
print("=" * 60)
scenarios = [
    ("Day",     2,  "Shared", "High",   25000, "Low risk expected"),
    ("Evening", 6,  "Alone",  "Medium", 15000, "Medium risk expected"),
    ("Night",   12, "Alone",  "Low",    8000,  "Higher risk expected"),
]
for time, dist, arr, safety, budget, label in scenarios:
    r = evaluate_risk(time, dist, arr, safety, budget)
    print(f"{label}: {time}/{dist}km/{arr}/{safety}/KES {budget}")
    print(f"  -> Level: {r.level}, Score: {r.score}/9")
    for f in r.factors:
        print(f"     - {f}")

print()
print("=" * 60)
print("TEST 5 — Issue 2: Conversation memory stores session history")
print("=" * 60)
from app.api.routes import _conversation_store

print("Sessions before request:", list(_conversation_store.keys()))

# This will fail at AI call (no real key) but memory logic runs before that
r = client.post('/api/housing-recommendations', json={
    'location': 'Kisumu',
    'destination': 'Kisumu CBD',
    'distance': 3,
    'time': 'Day',
    'budget': 18000,
    'safety': 'Medium',
    'arrangement': 'Alone',
    'query': '',
    'session_id': 'amina-session'
})
print("Sessions after request:", list(_conversation_store.keys()))
history = _conversation_store.get('amina-session', [])
print(f"Messages stored for 'amina-session': {len(history)}")
if history:
    print("First stored message role:", history[0]['role'])
    print("First stored message preview:", history[0]['content'][:100])

print()
print("=" * 60)
print("TEST 6 — Issue 5: Path traversal blocked in main.py")
print("=" * 60)
from pathlib import Path
frontend_path = Path("../frontend/build").resolve()
test_paths = [
    "index.html",
    "../../backend/.env",
    "../../../Windows/System32/drivers/etc/hosts",
]
for p in test_paths:
    resolved = (frontend_path / p).resolve()
    safe = str(resolved).startswith(str(frontend_path))
    print(f"Path: '{p}'")
    print(f"  Resolved: {resolved}")
    print(f"  Safe (stays inside frontend): {safe}")

print()
print("All tests complete.")

# Housing Safety Advisory Agent - Backend

## Structure

```
backend/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── api/                  # API routes
│   │   ├── __init__.py
│   │   └── routes.py         # Housing recommendation endpoints
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   └── housing_service.py # Housing advisory service
│   ├── ai/                   # AI provider abstraction
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract base class
│   │   ├── factory.py        # Provider factory
│   │   ├── gemini_provider.py
│   │   └── openai_provider.py
│   ├── schemas/              # Data models
│   │   ├── __init__.py
│   │   └── housing_models.py # Pydantic models
│   └── config/               # Configuration
│       ├── __init__.py
│       └── settings.py       # App settings
├── server.py                 # Entry point
└── requirements.txt          # Dependencies
```

## Setup

1. Create virtual environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in root `.env`:
```bash
AI_PROVIDER=openai  # or gemini
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key
```

4. Run the server:
```bash
python3 server.py
```

## API Endpoints

- `POST /api/housing-recommendations` - Get housing recommendations
- `GET /api/health` - Health check

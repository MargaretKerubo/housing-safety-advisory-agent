# Housing Safety Advisory AI Agent

An explainable, AI-assisted decision-support agent for housing evaluation.

## Project Structure

```
housing-safety-advisory-agent/
├── backend/              # Flask API server
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── services/    # Business logic
│   │   ├── ai/          # AI provider abstraction
│   │   ├── schemas/     # Data models
│   │   └── config/      # Configuration
│   ├── server.py        # Entry point
│   └── requirements.txt
├── frontend/            # React application
│   ├── src/
│   │   ├── components/
│   │   ├── utils/
│   │   └── styles/
│   └── package.json
├── docs/                # Documentation
├── .env                 # Environment variables
└── README.md
```

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python server.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Configuration

Create `.env` in the root directory:

```bash
# AI Provider
AI_PROVIDER=openai  # or gemini
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key

# Server
DEBUG=False
HOST=0.0.0.0
PORT=5000
```

## Architecture

- **Backend**: Flask REST API with service layer architecture
- **Frontend**: React SPA with Bootstrap UI
- **AI Layer**: Provider abstraction supporting Gemini and OpenAI
- **Data Models**: Pydantic schemas for validation

## Development

See individual README files in `backend/` and `frontend/` directories for detailed setup instructions.

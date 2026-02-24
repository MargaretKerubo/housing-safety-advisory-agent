# Housing Safety Advisory AI Agent

An explainable, AI-assisted decision-support agent that helps users evaluate housing options by reasoning over situational safety trade-offs.

## Project Structure

```
housing-safety-advisory-agent/
├── backend/              # Flask API server
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── services/    # Business logic
│   │   ├── ai/          # AI provider abstraction (Gemini/OpenAI)
│   │   ├── schemas/     # Pydantic data models
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
├── tests/               # Test files
├── .env                 # Environment variables (not in git)
└── .env.example         # Environment template

```

## Quick Start

### 1. Environment Setup

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
nano .env
```

```bash
# AI Provider: gemini or openai
AI_PROVIDER=openai

# API Keys
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 server.py
```

Backend runs on `http://localhost:5000`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

### 4. Quick Start (Both at Once)

```bash
./start_dev.sh
```

This script opens both backend and frontend in separate terminals.

## Features

- **Explainable Decision Support**: Clear reasoning for every recommendation
- **Situational Safety Analysis**: Evaluates commute patterns, travel times, and living context
- **Budget-Conscious Trade-offs**: Balances safety considerations with affordability
- **Ethical Guardrails**: Refuses and reframes unsafe or biased queries
- **AI Provider Abstraction**: Seamlessly switch between Gemini and OpenAI
- **Modern UI**: React frontend with Bootstrap components

## Architecture

- **Backend**: Flask REST API with service layer architecture
- **Frontend**: React SPA with responsive design
- **AI Layer**: Provider abstraction supporting multiple AI services
- **Data Models**: Pydantic schemas for validation

## API Endpoints

- `POST /api/housing-recommendations` - Get housing recommendations
- `GET /api/health` - Health check

## Development

See individual README files:
- `backend/README.md` - Backend setup and architecture
- `docs/AI_PROVIDER_ABSTRACTION.md` - AI provider documentation

## SDG Alignment

This project supports **UN SDG 11: Sustainable Cities and Communities** by promoting informed, inclusive housing decision-making without stigmatizing communities.

## Authors

- Flovian Atieno
- Anthony Oduor
- Stephen Oginga
- Margaret Kerubo
- Michelle Wanjiru

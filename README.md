
# Housing Safety Advisory Agent with React Frontend

An AI-powered decision-support agent that helps users evaluate housing options by reasoning over safety-related trade-offs such as commute patterns, time of travel, budget constraints, and situational risk factors. Features a React frontend with authentication and a Python Flask backend.

## Features

- **AI-Powered Recommendations**: Uses Google Gemini to provide intelligent housing recommendations
- **Safety Analysis**: Evaluates commute patterns, travel times, and situational risk factors
- **Budget-Conscious**: Helps balance safety considerations with budget constraints
- **Explainable Decisions**: Provides clear reasoning for each recommendation
- **Location-Based**: Currently optimized for Kisumu, Kenya housing market
- **Modular Architecture**: Clean separation of concerns with well-defined components
- **React Frontend**: Modern UI with authentication and responsive design
- **Python Backend**: Flask API serving the housing recommendation engine

## Prerequisites

- **Python 3.10 or higher**
- **Node.js and npm** (for the React frontend)
- **Google Gemini API Key** - [Get API Key](https://aistudio.google.com/)

## Quick Start

### 1. Set up your environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root directory:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API key
nano .env  # Or use your preferred editor
```

### 3. Install and Build the Frontend

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Build the React app
npm run build
```

### 4. Run the Application

```bash
# From the project root directory
python api_server.py
```

The application will be available at `http://localhost:5000`

## Development

### Frontend Development

```bash
# In one terminal, start the React development server
cd frontend
npm start

# In another terminal, start the Python backend
python api_server.py
```

Note: During development, the React app will run on `http://localhost:3000` and proxy API requests to the Flask backend.

### Backend Development

The backend API endpoints are:

- `POST /api/housing-recommendations` - Get housing recommendations
- `GET /api/health` - Health check

## Project Structure

```
housing-safety-advisory-agent/
├── README.md                    # Project documentation
├── api_server.py               # Flask API server
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment variables
├── docs/                      # Documentation and schemas
│   └── response_schema.json   # Example response format
├── src/                       # Housing agent source code
│   ├── __init__.py
│   ├── core/                  # Core business logic
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration and API client setup
│   │   ├── triage.py          # Input analysis and validation
│   │   ├── gather_details.py  # Information gathering logic
│   │   ├── research.py        # Neighborhood research logic
│   │   ├── presentation.py    # Response formatting
│   │   └── agent_orchestrator.py # Main agent workflow
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   └── housing_models.py  # Pydantic models
│   ├── tools/                 # External tools (future use)
│   │   └── __init__.py
│   ├── agents/                # Specialized agents (future use)
│   │   └── __init__.py
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── chat_utils.py      # Interactive chat utilities
├── frontend/                  # React frontend
│   ├── public/                # Public assets
│   ├── src/                   # React source code
│   │   ├── App.js             # Main application component
│   │   ├── components/        # React components
│   │   │   ├── AuthFlow.js    # Authentication component
│   │   │   └── MainApp.js     # Main application component
│   │   ├── utils/             # Utility functions
│   │   │   └── apiService.js  # API service
│   │   └── styles/            # CSS styles
│   ├── package.json           # Frontend dependencies
│   └── build/                 # Built frontend assets
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_models.py         # Model tests
│   └── test_structure.py      # Structural verification tests
└── .env                       # Environment variables (not tracked)
```

## Architecture Overview

The application follows a modular architecture with clear separation of concerns:

- **Frontend**: React application with Bootstrap components for responsive UI
- **Backend**: Flask API serving the housing recommendation engine
- **Models**: Defines data structures using Pydantic for validation
- **Core**: Contains the main business logic and AI integration
- **Utils**: Provides helper functions and utilities

## License

This project is aligned with UN Sustainable Development Goal 11 (Sustainable Cities and Communities).
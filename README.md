# Housing Safety Advisory Agent

An AI-powered decision-support agent that helps users evaluate housing options by reasoning over safety-related trade-offs such as commute patterns, time of travel, budget constraints, and situational risk factors. Designed as an ethical, explainable advisory system aligned with SDG 11.

## Features

- **AI-Powered Recommendations**: Uses Google Gemini to provide intelligent housing recommendations
- **Safety Analysis**: Evaluates commute patterns, travel times, and situational risk factors
- **Budget-Conscious**: Helps balance safety considerations with budget constraints
- **Explainable Decisions**: Provides clear reasoning for each recommendation
- **Location-Based**: Currently optimized for Kisumu, Kenya housing market
- **Modular Architecture**: Clean separation of concerns with well-defined components

## Prerequisites

- **Python 3.10 or higher**
- **Google Gemini API Key** - [Get API Key](https://aistudio.google.com/)

## Quick Start

### 1. Set up your environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
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

## How to Run the Project

```bash
# Run the main application
python main.py
```

## Dependencies

- `google-genai>=0.1.0` - Google Gemini AI SDK
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment variable management

## Project Structure

```
housing-safety-advisory-agent/
├── README.md                    # Project documentation
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
├── .env.example               # Example environment variables
├── docs/                      # Documentation and schemas
│   └── response_schema.json   # Example response format
├── src/                       # Source code
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
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_models.py         # Model tests
└── .env                       # Environment variables (not tracked)
```

## Architecture Overview

The application follows a modular architecture with clear separation of concerns:

- **Models**: Defines data structures using Pydantic for validation
- **Core**: Contains the main business logic and AI integration
- **Utils**: Provides helper functions and utilities
- **Agents**: Will contain specialized AI agents (future expansion)
- **Tools**: Will contain external integrations (future expansion)

## License

This project is aligned with UN Sustainable Development Goal 11 (Sustainable Cities and Communities).

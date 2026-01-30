# Housing Safety Advisory Agent

An AI-powered decision-support agent that helps users evaluate housing options by reasoning over safety-related trade-offs such as commute patterns, time of travel, budget constraints, and situational risk factors. Designed as an ethical, explainable advisory system aligned with SDG 11.

## Features

- **AI-Powered Recommendations**: Uses Google Gemini to provide intelligent housing recommendations
- **Safety Analysis**: Evaluates commute patterns, travel times, and situational risk factors
- **Budget-Conscious**: Helps balance safety considerations with budget constraints
- **Explainable Decisions**: Provides clear reasoning for each recommendation
- **Location-Based**: Currently optimized for Kisumu, Kenya housing market

## Prerequisites

- **Conda** (Miniconda or Anaconda) - [Install Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/)
- **Python 3.10 or higher**
- **Google Gemini API Key** - [Get API Key](https://aistudio.google.com/)

## Conda Environment Setup

### 1. Create a New Conda Environment

```bash
# Create a new conda environment with Python 3.10
conda create -n housing-safety python=3.10 -y
```

### 2. Activate the Environment

```bash
# On Linux/Mac
conda activate housing-safety

# On Windows
conda activate housing-safety
```

### 3. Install Dependencies

```bash
# Navigate to the project directory
cd housing-safety-advisory-agent

# Install required Python packages
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root directory:

```bash
# Create .env file
touch .env

# Add your Gemini API key to .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

Or manually create `.env` with:
```
GEMINI_API_KEY=your_google_gemini_api_key_here
```

## How to Run the Project

### 1. Activate the Conda Environment

```bash
conda activate housing-safety
```

### 2. Set Up Your API Key

Make sure your `.env` file is set up with your Gemini API key, or export it directly:

```bash
# Option A: Using .env file (recommended)
# Make sure .env file exists with your GEMINI_API_KEY

# Option B: Export directly
export GEMINI_API_KEY="your_api_key_here"
```

### 3. Run the Application

```bash
# Run the main application
python gemini_main.py
```

## Dependencies

- `google-genai>=0.1.0` - Google Gemini AI SDK
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment variable management

## Project Structure

```
housing-safety-advisory-agent/
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── gemini_main.py              # Main application script
├── docs/response_schema.json  # Example response format
└── .env                        # Environment variables (create this)
```

## License

This project is aligned with UN Sustainable Development Goal 11 (Sustainable Cities and Communities).

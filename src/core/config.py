from dotenv import load_dotenv
from src.ai import get_ai_provider

# Load environment variables
load_dotenv()

# Initialize AI provider (Gemini or OpenAI based on AI_PROVIDER env var)
ai_provider = get_ai_provider()
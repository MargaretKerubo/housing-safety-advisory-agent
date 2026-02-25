import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / '.env')

class Config:
    """Application configuration."""
    
    # Flask
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # AI Provider
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini').lower()
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Frontend
    FRONTEND_BUILD_PATH = os.getenv('FRONTEND_BUILD_PATH', str(project_root / 'frontend' / 'build'))

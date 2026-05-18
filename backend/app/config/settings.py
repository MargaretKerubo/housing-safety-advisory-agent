import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / '.env')

class Config:
    """Application configuration."""
    
    # Flask / Security
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-for-development-only')
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{project_root}/housing_agent.db")
    
    # AI Provider
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini').lower()
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Frontend
    FRONTEND_BUILD_PATH = os.getenv('FRONTEND_BUILD_PATH', str(project_root / 'frontend' / 'build'))

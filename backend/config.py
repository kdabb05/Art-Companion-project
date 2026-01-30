"""Configuration management for Art Studio Companion."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database path as string
DB_PATH = str(DATA_DIR / "studio.db")


class Config:
    """Application configuration."""
    
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    
    # Database - use absolute path string
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenRouter / LLM
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    LETTA_LLM_ENDPOINT = os.getenv("LETTA_LLM_ENDPOINT", "https://openrouter.ai/api/v1")
    LETTA_MODEL = os.getenv("LETTA_MODEL", "anthropic/claude-3-haiku")
    
    # Uploads
    UPLOAD_FOLDER = DATA_DIR / "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

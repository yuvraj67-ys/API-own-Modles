from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "My AI Hub API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    API_SECRET_KEY: str = "change-this-in-production!"
    ADMIN_KEYS: list = ["admin-super-key-123"]  # Add your admin keys
    
    # Database
    DATABASE_URL: str = "sqlite:///./myai.db"
    
    # Hugging Face (Free API)
    HF_API_TOKEN: str = ""  # Get from https://huggingface.co/settings/tokens
    HF_IMAGE_MODEL: str = "stabilityai/stable-diffusion-2-1"
    HF_SONG_MODEL: str = "facebook/musicgen-small"
    
    # Limits (per user per day)
    FREE_DAILY_IMAGE_GEN: int = 10
    FREE_DAILY_IMAGE_EDIT: int = 5
    FREE_DAILY_SONG_GEN: int = 3
    
    # Storage
    UPLOAD_FOLDER: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
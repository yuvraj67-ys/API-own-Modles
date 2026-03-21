cat > config.py << 'EOF'
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = os.getenv("APP_NAME", "My AI Hub API")
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Security
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "change-me-in-production")
    ADMIN_KEYS: list = os.getenv("ADMIN_KEYS", "admin-key").split(",")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./myai.db")
    
    # Hugging Face
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")
    HF_IMAGE_MODEL: str = os.getenv("HF_IMAGE_MODEL", "stabilityai/stable-diffusion-2-1")
    HF_SONG_MODEL: str = os.getenv("HF_SONG_MODEL", "facebook/musicgen-small")
    
    # Limits (free tier)
    FREE_DAILY_IMAGE_GEN: int = int(os.getenv("FREE_DAILY_IMAGE_GEN", "10"))
    FREE_DAILY_IMAGE_EDIT: int = int(os.getenv("FREE_DAILY_IMAGE_EDIT", "5"))
    FREE_DAILY_SONG_GEN: int = int(os.getenv("FREE_DAILY_SONG_GEN", "3"))
    
    # Storage
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "./uploads")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
EOF

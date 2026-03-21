from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = os.getenv("APP_NAME", "My AI Hub API")
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Security - FIXED: Use str, split manually
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "change-me")
    _ADMIN_KEYS_STR: str = os.getenv("ADMIN_KEYS", "admin-key")
    
    @property
    def ADMIN_KEYS(self) -> List[str]:
        return [k.strip() for k in self._ADMIN_KEYS_STR.split(",") if k.strip()]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./myai.db")
    
    # Hugging Face
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")
    HF_IMAGE_MODEL: str = os.getenv("HF_IMAGE_MODEL", "stabilityai/stable-diffusion-2-1")
    HF_SONG_MODEL: str = os.getenv("HF_SONG_MODEL", "facebook/musicgen-small")
    
    # Limits
    FREE_DAILY_IMAGE_GEN: int = int(os.getenv("FREE_DAILY_IMAGE_GEN", "10"))
    FREE_DAILY_IMAGE_EDIT: int = int(os.getenv("FREE_DAILY_IMAGE_EDIT", "5"))
    FREE_DAILY_SONG_GEN: int = int(os.getenv("FREE_DAILY_SONG_GEN", "3"))
    
    # Storage
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "./uploads")
    MAX_FILE_SIZE_MB: int = int(os.getenv("AX_FILE_SIZE_MB", "10"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

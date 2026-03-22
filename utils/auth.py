from fastapi import Header, HTTPException, status
from typing import Optional
from models import SessionLocal, User, APIKey
from config import settings
import secrets

# Unlimited keys list (bypass all limits)
UNLIMITED_KEYS = [
    "unlimited-key-2026-vip",
    "sk-unlimited-access-key",
    "admin-master-key-2026"
]

def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    # Check unlimited keys first
    if x_api_key in UNLIMITED_KEYS:
        return "unlimited_user"
    
    # Check admin keys
    admin_keys = [k.strip() for k in settings._ADMIN_KEYS_STR.split(",") if k.strip()]
    if x_api_key in admin_keys:
        return "admin_user"
    
    # Check database for user keys
    db = SessionLocal()
    try:
        key_record = db.query(APIKey).filter(
            APIKey.key == x_api_key,
            APIKey.is_active == True
        ).first()
        if not key_record:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        user = db.query(User).filter(User.id == key_record.user_id).first()
        if user and user.is_banned:
            raise HTTPException(status_code=403, detail="User banned")
        
        return key_record.user_id
    finally:
        db.close()

def is_unlimited(api_key: str) -> bool:
    """Check if API key has unlimited access"""
    return api_key in UNLIMITED_KEYS

def generate_api_key() -> str:
    return f"sk-{secrets.token_urlsafe(32)}"

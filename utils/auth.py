from fastapi import Header, HTTPException
from typing import Optional
from models import SessionLocal, User, APIKey
import secrets

# UNLIMITED KEYS LIST
UNLIMITED_KEYS = [
    "admin-master-key-2026",
    "unlimited-key-2026-vip",
    "sk-unlimited-access-key"
]

def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    if x_api_key in UNLIMITED_KEYS:
        return "unlimited_user"
    
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

def is_admin(x_api_key: Optional[str] = Header(None)) -> bool:
    if not x_api_key:
        return False
    return x_api_key in UNLIMITED_KEYS

def generate_api_key() -> str:
    return f"sk-{secrets.token_urlsafe(32)}"

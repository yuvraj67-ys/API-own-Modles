from fastapi import Header, HTTPException, status
from typing import Optional
from models import SessionLocal, User, APIKey
from config import settings
import secrets

def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key and return user_id"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    # Allow admin keys for all endpoints (for testing)
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
        
        # Check if user is banned
        user = db.query(User).filter(User.id == key_record.user_id).first()
        if user and user.is_banned:
            raise HTTPException(status_code=403, detail="User banned")
        
        return key_record.user_id
    finally:
        db.close()

def generate_api_key() -> str:
    """Generate secure random API key"""
    return f"sk-{secrets.token_urlsafe(32)}"

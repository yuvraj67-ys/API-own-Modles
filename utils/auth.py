from fastapi import Header, HTTPException, status
from typing import Optional
from models import SessionLocal, User, APIKey
from config import settings
import secrets

def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key and return user_id"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Use X-API-Key header."
        )
    
    db = SessionLocal()
    try:
        key_record = db.query(APIKey).filter(
            APIKey.key == x_api_key,
            APIKey.is_active == True
        ).first()
        
        if not key_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive API key"
            )
        
        # Check if user is banned
        user = db.query(User).filter(User.id == key_record.user_id).first()
        if user and user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is banned"
            )
        
        return key_record.user_id
    finally:
        db.close()

def is_admin(api_key: Optional[str] = Header(None)) -> bool:
    """Check if API key belongs to admin"""
    return api_key in settings.ADMIN_KEYS

def generate_api_key() -> str:
    """Generate secure random API key"""
    return f"sk-{secrets.token_urlsafe(32)}"

def create_user_api_key(user_id: str) -> str:
    """Create new API key for user"""
    from models import APIKey, SessionLocal
    
    db = SessionLocal()
    try:
        # Revoke old keys (optional - keep only one active)
        db.query(APIKey).filter(
            APIKey.user_id == user_id
        ).update({"is_active": False})
        
        # Create new key
        new_key = generate_api_key()
        db_key = APIKey(user_id=user_id, key=new_key)
        db.add(db_key)
        db.commit()
        return new_key
    finally:
        db.close()
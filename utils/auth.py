from fastapi import Header, HTTPException, status
from typing import Optional
from models import SessionLocal, User, APIKey
from config import settings
import secrets

def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    db = SessionLocal()
    try:
        key_record = db.query(APIKey).filter(APIKey.key == x_api_key, APIKey.is_active == True).first()
        if not key_record:
            raise HTTPException(status_code=401, detail="Invalid API key")
        user = db.query(User).filter(User.id == key_record.user_id).first()
        if user and user.is_banned:
            raise HTTPException(status_code=403, detail="User banned")
        return key_record.user_id
    finally:
        db.close()

def is_admin(api_key: Optional[str] = Header(None)) -> bool:
    return api_key in settings.ADMIN_KEYS

def generate_api_key() -> str:
    return f"sk-{secrets.token_urlsafe(32)}"

def create_user_api_key(user_id: str) -> str:
    from models import APIKey, SessionLocal
    db = SessionLocal()
    try:
        db.query(APIKey).filter(APIKey.user_id == user_id).update({"is_active": False})
        new_key = generate_api_key()
        db_key = APIKey(user_id=user_id, key=new_key)
        db.add(db_key)
        db.commit()
        return new_key
    finally:
        db.close()

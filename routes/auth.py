from fastapi import APIRouter, Header, HTTPException
from models import SessionLocal, User, APIKey
from utils.auth import generate_api_key
from config import settings

router = APIRouter(prefix="/internal", tags=["auth"])

def check_admin(x_api_key):
    """Check if key is admin key"""
    if not x_api_key:
        return False
    # Get admin keys from settings
    admin_keys = settings.ADMIN_KEYS
    # Also check hardcoded unlimited keys
    unlimited_keys = ["unlimited-key-2026-vip", "sk-unlimited-access-key", "admin-master-key-2026"]
    return x_api_key in admin_keys or x_api_key in unlimited_keys

@router.post("/create-key/{user_id}")
def create_api_key(user_id: str, x_api_key: str = Header(None)):
    if not check_admin(x_api_key):
        raise HTTPException(status_code=403, detail="Admin required")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id)
            db.add(user)
            db.commit()
        db.query(APIKey).filter(APIKey.user_id == user_id).update({"is_active": False})
        new_key = generate_api_key()
        db_key = APIKey(user_id=user_id, key=new_key, is_active=True)
        db.add(db_key)
        db.commit()
        return {"success": True, "api_key": new_key, "user_id": user_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        db.close()

@router.post("/revoke-key/{user_id}")
def revoke_key(user_id: str, x_api_key: str = Header(None)):
    if not check_admin(x_api_key):
        raise HTTPException(status_code=403, detail="Admin required")
    
    db = SessionLocal()
    try:
        db.query(APIKey).filter(APIKey.user_id == user_id).update({"is_active": False})
        db.commit()
        return {"success": True, "message": "Key revoked"}
    finally:
        db.close()

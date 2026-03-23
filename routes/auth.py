from fastapi import APIRouter, Header, HTTPException
from models import SessionLocal, User, APIKey
from utils.auth import generate_api_key

# UNLIMITED ADMIN KEYS
ADMIN_KEYS = [
    "admin-master-key-2026",
    "unlimited-key-2026-vip",
    "sk-unlimited-access-key"
]

router = APIRouter(prefix="/internal", tags=["auth"])

@router.post("/create-key/{user_id}")
def create_api_key(user_id: str, x_api_key: str = Header(None)):
    if x_api_key not in ADMIN_KEYS:
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
    if x_api_key not in ADMIN_KEYS:
        raise HTTPException(status_code=403, detail="Admin required")
    
    db = SessionLocal()
    try:
        db.query(APIKey).filter(APIKey.user_id == user_id).update({"is_active": False})
        db.commit()
        return {"success": True, "message": "Key revoked"}
    finally:
        db.close()

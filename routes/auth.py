from fastapi import APIRouter, Depends, HTTPException
from models import SessionLocal, User, APIKey
from utils.auth import generate_api_key, is_admin

router = APIRouter(prefix="/internal", tags=["auth"])

@router.post("/create-key/{user_id}")
def create_api_key(user_id: str, api_key: str = Depends(is_admin)):
    if not is_admin(api_key):
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
        db_key = APIKey(user_id=user_id, key=new_key)
        db.add(db_key)
        db.commit()
        return {"success": True, "api_key": new_key, "user_id": user_id}
    finally:
        db.close()

@router.post("/revoke-key/{user_id}")
def revoke_key(user_id: str, api_key: str = Depends(is_admin)):
    if not is_admin(api_key):
        raise HTTPException(status_code=403, detail="Admin required")
    db = SessionLocal()
    try:
        db.query(APIKey).filter(APIKey.user_id == user_id).update({"is_active": False})
        db.commit()
        return {"success": True, "message": "Key revoked"}
    finally:
        db.close()

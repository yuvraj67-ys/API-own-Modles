from fastapi import APIRouter, Header, HTTPException, Depends
from models import SessionLocal, User, APIKey
from utils.auth import generate_api_key
from config import settings

router = APIRouter(prefix="/internal", tags=["auth"])

def get_admin_key(x_api_key: str = Header(None)) -> str:
    """Dependency: Verify admin key and return it"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    # Check if key is in admin list
    admin_keys = [k.strip() for k in settings._ADMIN_KEYS_STR.split(",") if k.strip()]
    if x_api_key not in admin_keys:
        raise HTTPException(status_code=403, detail="Admin required")
    
    return x_api_key

@router.post("/create-key/{user_id}")
def create_api_key(user_id: str, admin_key: str = Depends(get_admin_key)):
    """Create API key for user (admin only)"""
    db = SessionLocal()
    try:
        # Create user if not exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id)
            db.add(user)
            db.commit()
        
        # Revoke old keys for this user
        db.query(APIKey).filter(APIKey.user_id == user_id).update({"is_active": False})
        
        # Generate new key
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
def revoke_key(user_id: str, admin_key: str = Depends(get_admin_key)):
    """Revoke user's API key (admin only)"""
    db = SessionLocal()
    try:
        db.query(APIKey).filter(APIKey.user_id == user_id).update({"is_active": False})
        db.commit()
        return {"success": True, "message": "Key revoked"}
    finally:
        db.close()

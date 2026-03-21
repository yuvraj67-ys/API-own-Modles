from fastapi import APIRouter, Depends, HTTPException
from models import SessionLocal, User
from utils.auth import is_admin

router = APIRouter(prefix="/admin/api", tags=["admin"])

@router.get("/stats")
def admin_stats(api_key: str = Depends(is_admin)):
    if not is_admin(api_key):
        raise HTTPException(status_code=403, detail="Admin required")
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_banned == False).count()
        return {"total_users": total_users, "active_users": active_users}
    finally:
        db.close()

@router.get("/users")
def admin_users(api_key: str = Depends(is_admin)):
    if not is_admin(api_key):
        raise HTTPException(status_code=403, detail="Admin required")
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return {"users": [{"id": u.id, "plan": u.plan, "banned": u.is_banned} for u in users]}
    finally:
        db.close()

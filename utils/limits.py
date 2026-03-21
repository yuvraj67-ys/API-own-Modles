from models import SessionLocal, Usage
from datetime import datetime
from config import settings

def get_today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def check_limit(user_id: str, tool_name: str, db=None) -> tuple[bool, int, int]:
    """
    Check if user has remaining usage for today
    Returns: (allowed: bool, used: int, limit: int)
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        # Get limits based on tool
        limits = {
            "imagegen": settings.FREE_DAILY_IMAGE_GEN,
            "imageedit": settings.FREE_DAILY_IMAGE_EDIT,
            "songgen": settings.FREE_DAILY_SONG_GEN,
        }
        daily_limit = limits.get(tool_name, 10)
        
        # Get today's usage
        today = get_today_str()
        usage = db.query(Usage).filter(
            Usage.user_id == user_id,
            Usage.tool_name == tool_name,
            Usage.date == today
        ).first()
        
        used_count = usage.count if usage else 0
        allowed = used_count < daily_limit
        
        return allowed, used_count, daily_limit
    finally:
        if close_db:
            db.close()

def increment_usage(user_id: str, tool_name: str, db=None):
    """Increment usage counter for user+tool+today"""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        today = get_today_str()
        
        # Try to update existing record
        result = db.query(Usage).filter(
            Usage.user_id == user_id,
            Usage.tool_name == tool_name,
            Usage.date == today
        ).update({"count": Usage.count + 1})
        
        # If no record exists, create new one
        if result == 0:
            new_usage = Usage(
                user_id=user_id,
                tool_name=tool_name,
                date=today,
                count=1
            )
            db.add(new_usage)
        
        db.commit()
    finally:
        if close_db:
            db.close()

def get_usage_summary(user_id: str) -> dict:
    """Get all usage stats for user"""
    db = SessionLocal()
    try:
        today = get_today_str()
        tools = ["imagegen", "imageedit", "songgen"]
        summary = {}
        
        for tool in tools:
            allowed, used, limit = check_limit(user_id, tool, db)
            summary[tool] = {
                "used": used,
                "limit": limit,
                "remaining": max(0, limit - used),
                "reset_at": f"{today}T23:59:59Z"
            }
        
        return summary
    finally:
        db.close()
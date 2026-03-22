from models import SessionLocal, Usage
from datetime import datetime
from config import settings

UNLIMITED_KEYS = [
    "unlimited-key-2026-vip",
    "sk-unlimited-access-key",
    "admin-master-key-2026"
]

def get_today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def check_limit(user_id: str, tool_name: str, db=None, api_key: str = None):
    if api_key and api_key in UNLIMITED_KEYS:
        return True, 0, 999999
    
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        limits = {
            "imagegen": settings.FREE_DAILY_IMAGE_GEN,
            "imageedit": settings.FREE_DAILY_IMAGE_EDIT,
            "songgen": settings.FREE_DAILY_SONG_GEN,
        }
        daily_limit = limits.get(tool_name, 10)
        today = get_today_str()
        usage = db.query(Usage).filter(
            Usage.user_id == user_id,
            Usage.tool_name == tool_name,
            Usage.date == today
        ).first()
        used_count = usage.count if usage else 0
        return (used_count < daily_limit), used_count, daily_limit
    finally:
        if close_db:
            db.close()

def increment_usage(user_id: str, tool_name: str, db=None, api_key: str = None):
    if api_key and api_key in UNLIMITED_KEYS:
        return
    
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        today = get_today_str()
        result = db.query(Usage).filter(
            Usage.user_id == user_id,
            Usage.tool_name == tool_name,
            Usage.date == today
        ).update({"count": Usage.count + 1})
        if result == 0:
            new_usage = Usage(user_id=user_id, tool_name=tool_name, date=today, count=1)
            db.add(new_usage)
        db.commit()
    finally:
        if close_db:
            db.close()

def get_usage_summary(user_id: str, api_key: str = None):
    if api_key and api_key in UNLIMITED_KEYS:
        return {
            "imagegen": {"used": 0, "limit": 999999, "remaining": 999999},
            "imageedit": {"used": 0, "limit": 999999, "remaining": 999999},
            "songgen": {"used": 0, "limit": 999999, "remaining": 999999},
        }
    
    db = SessionLocal()
    try:
        tools = ["imagegen", "imageedit", "songgen"]
        summary = {}
        for tool in tools:
            allowed, used, limit = check_limit(user_id, tool, db, api_key)
            summary[tool] = {"used": used, "limit": limit, "remaining": max(0, limit - used)}
        return summary
    finally:
        db.close()

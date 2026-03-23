from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from models import init_db
import uvicorn
import os

from routes import image, song, auth, admin

# UNLIMITED KEYS - HARDCODED
UNLIMITED_KEYS = [
    "admin-master-key-2026",
    "unlimited-key-2026-vip",
    "sk-unlimited-access-key"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("API started")
    yield

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

upload_path = os.getenv("RENDER_UPLOAD_PATH", settings.UPLOAD_FOLDER)
if os.path.exists(upload_path):
    app.mount("/files", StaticFiles(directory=upload_path), name="files")

app.include_router(image.router)
app.include_router(song.router)
app.include_router(auth.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"status": "online", "app": settings.APP_NAME, "version": settings.APP_VERSION}

@app.get("/ping")
def ping():
    return {"pong": True, "status": "healthy"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/v1/usage")
def get_usage(x_api_key: str = Header(None)):
    # UNLIMITED CHECK - HARDCODED
    if x_api_key in UNLIMITED_KEYS:
        return {
            "imagegen": {"used": 0, "limit": 999999, "remaining": 999999},
            "imageedit": {"used": 0, "limit": 999999, "remaining": 999999},
            "songgen": {"used": 0, "limit": 999999, "remaining": 999999},
            "access": "UNLIMITED"
        }
    
    # Regular user check
    from utils.limits import get_usage_summary
    from utils.auth import verify_api_key
    try:
        user_id = verify_api_key(x_api_key)
        return get_usage_summary(user_id, api_key=x_api_key)
    except:
        raise HTTPException(status_code=401, detail="Invalid API key")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from models import init_db
import uvicorn
import os

from routes import image, song, auth, admin

# Unlimited Keys List
UNLIMITED_KEYS = [
    "admin-master-key-2026",
    "unlimited-key-2026-vip",
    "sk-unlimited-access-key"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} started")
    yield
    print("👋 Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files
upload_path = os.getenv("RENDER_UPLOAD_PATH", settings.UPLOAD_FOLDER)
if os.path.exists(upload_path):
    app.mount("/files", StaticFiles(directory=upload_path), name="files")

# Include Routersapp.include_router(image.router)
app.include_router(song.router)
app.include_router(auth.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/ping")
def ping():
    return {"pong": True, "status": "healthy"}

@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected"}

@app.get("/api/v1/usage")
def get_usage(x_api_key: str = Header(None)):
    from utils.limits import get_usage_summary
    from utils.auth import verify_api_key
    
    # Check unlimited keys
    if x_api_key in UNLIMITED_KEYS:
        return {
            "imagegen": {"used": 0, "limit": 999999, "remaining": 999999},
            "imageedit": {"used": 0, "limit": 999999, "remaining": 999999},
            "songgen": {"used": 0, "limit": 999999, "remaining": 999999},
            "access": "unlimited"
        }
    
    # For regular user keys
    try:
        user_id = verify_api_key(x_api_key)
        return get_usage_summary(user_id, api_key=x_api_key)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid API key: {str(e)}")

@app.get("/docs")
def api_docs():
    return {"message": "Visit /docs for interactive API documentation"}

if __name__ == "__main__":    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=settings.DEBUG
    )

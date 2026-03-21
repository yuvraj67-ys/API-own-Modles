from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from models import init_db, get_db
from utils.auth import verify_api_key, is_admin
import uvicorn

# Import routers
from routes import image, song, auth, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB
    init_db()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} started")
    yield
    # Shutdown: Cleanup if needed
    print("👋 Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Your personal AI Hub - Image & Song Generation API",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for generated content
app.mount("/files", StaticFiles(directory=settings.UPLOAD_FOLDER), name="files")

# Include routers
app.include_router(image.router)
app.include_router(song.router)
app.include_router(auth.router)
app.include_router(admin.router)

# Health & Info endpoints
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
def get_user_usage(user_id: str = Depends(verify_api_key)):
    """Get current usage stats for authenticated user"""
    from utils.limits import get_usage_summary
    return get_usage_summary(user_id)

# Run with: uvicorn main:app --host 0.0.0.0 --port 8080
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=settings.DEBUG)
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from models import init_db
import uvicorn, os

from routes import image, song, auth, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} started")
    yield
    print("👋 Shutting down...")

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
    return {"status": "online", "app": settings.APP_NAME, "version": settings.APP_VERSION, "docs": "/docs"}

@app.get("/ping")
def ping():
    return {"pong": True, "status": "healthy"}

@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected"}

@app.get("/api/v1/usage")
def get_usage(user_id: str = Depends(lambda: "test")):
    from utils.limits import get_usage_summary
    return get_usage_summary(user_id)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=settings.DEBUG)

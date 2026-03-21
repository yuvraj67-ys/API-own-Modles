cat > utils/storage.py << 'EOF'
import os
import aiofiles
from pathlib import Path
from config import settings
from fastapi import HTTPException

UPLOAD_DIR = Path(os.getenv("RENDER_UPLOAD_PATH", settings.UPLOAD_FOLDER))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def save_generated_file(file_bytes: bytes, file_id: str, file_type: str) -> str:
    ext = ".png" if file_type == "image" else ".mp3"
    filename = f"{file_id}{ext}"
    filepath = UPLOAD_DIR / filename
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(file_bytes)
    domain = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8080")
    return f"{domain}/files/{filename}"

async def get_file(file_id: str) -> bytes:
    for ext in [".png", ".mp3"]:
        filepath = UPLOAD_DIR / f"{file_id}{ext}"
        if filepath.exists():
            async with aiofiles.open(filepath, "rb") as f:
                return await f.read()
    raise HTTPException(status_code=404, detail="File not found")
EOF

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from typing import Optional
from utils.auth import verify_api_key
from utils.limits import check_limit, increment_usage
from utils.hf_client import hf_client
from utils.storage import save_generated_file
import uuid

router = APIRouter(prefix="/api/v1", tags=["images"])

@router.post("/imagegen")
async def generate_image(
    prompt: str = Form(...),
    user_id: str = Depends(verify_api_key),
    aspect_ratio: str = Form("1:1"),
    x_api_key: Optional[str] = None
):
    # Pass API key to limit checker
    allowed, used, limit = check_limit(user_id, "imagegen", api_key=x_api_key)
    if not allowed:
        raise HTTPException(status_code=429, detail=f"Limit reached ({used}/{limit})")
    try:
        image_bytes = await hf_client.generate_image(prompt)
        file_id = str(uuid.uuid4())
        file_url = await save_generated_file(image_bytes, file_id, "image")
        increment_usage(user_id, "imagegen", api_key=x_api_key)
        return {"success": True, "image_url": file_url, "prompt": prompt, "usage": {"used": used+1, "limit": limit}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")

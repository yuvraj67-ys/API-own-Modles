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
    aspect_ratio: str = Form("1:1")
):
    """Generate image from text prompt"""
    
    # Check usage limit
    allowed, used, limit = check_limit(user_id, "imagegen")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit reached ({used}/{limit}). Resets at midnight UTC."
        )
    
    try:
        # Generate image via HF API
        image_bytes = await hf_client.generate_image(prompt)
        
        # Save file and get URL
        file_id = str(uuid.uuid4())
        file_url = await save_generated_file(image_bytes, file_id, "image")
        
        # Increment usage
        increment_usage(user_id, "imagegen")
        
        return {
            "success": True,
            "image_url": file_url,
            "prompt": prompt,
            "usage": {"used": used + 1, "limit": limit}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/imageedit")
async def edit_image(
    prompt: str = Form(...),
    image: UploadFile = File(...),
    user_id: str = Depends(verify_api_key),
    aspect_ratio: str = Form("1:1")
):
    """Edit/modify existing image"""
    
    # Validate file
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Check limit
    allowed, used, limit = check_limit(user_id, "imageedit")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit reached ({used}/{limit})"
        )
    
    try:
        # Read uploaded image
        image_bytes = await image.read()
        
        # Edit via HF API
        edited_bytes = await hf_client.edit_image(prompt, image_bytes)
        
        # Save and return
        file_id = str(uuid.uuid4())
        file_url = await save_generated_file(edited_bytes, file_id, "image")
        
        increment_usage(user_id, "imageedit")
        
        return {
            "success": True,
            "edited_url": file_url,
            "prompt": prompt,
            "usage": {"used": used + 1, "limit": limit}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Edit failed: {str(e)}")
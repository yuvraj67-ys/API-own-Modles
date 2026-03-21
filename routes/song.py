from fastapi import APIRouter, Depends, Form, HTTPException
from utils.auth import verify_api_key
from utils.limits import check_limit, increment_usage
from utils.hf_client import hf_client
from utils.storage import save_generated_file
import uuid

router = APIRouter(prefix="/api/v1", tags=["songs"])

@router.post("/songgen")
async def generate_song(
    prompt: str = Form(...),
    style: str = Form(""),
    model: str = Form(""),
    user_id: str = Depends(verify_api_key)
):
    """Generate music from text description"""
    
    # Check limit
    allowed, used, limit = check_limit(user_id, "songgen")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit reached ({used}/{limit})"
        )
    
    try:
        # Generate via HF MusicGen
        audio_bytes = await hf_client.generate_song(prompt, style, model or None)
        
        # Save file
        file_id = str(uuid.uuid4())
        file_url = await save_generated_file(audio_bytes, file_id, "audio")
        
        increment_usage(user_id, "songgen")
        
        return {
            "success": True,
            "audio_url": file_url,
            "prompt": prompt,
            "style": style,
            "duration_sec": 30,  # MusicGen default
            "usage": {"used": used + 1, "limit": limit}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.get("/songgen/presets")
def get_song_presets():
    """Get available music style presets"""
    return {"presets": hf_client.get_available_presets()}
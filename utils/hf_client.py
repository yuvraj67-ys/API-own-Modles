import httpx
from config import settings
from typing import Optional
import base64

class HFClient:
    # ✅ CORRECT 2026 HF ENDPOINT
    BASE_URL = "https://router.huggingface.co/hf-inference/models"
    
    def __init__(self, api_token: Optional[str] = None):
        self.token = api_token or settings.HF_API_TOKEN
        self.headers = {}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
        self.headers["Content-Type"] = "application/json"
    
    async def generate_image(self, prompt: str, model: Optional[str] = None) -> bytes:
        # ✅ Use working model (FLUX.1-Krea-dev or SDXL-Lightning)
        model_name = model or "ByteDance/SDXL-Lightning"
        url = f"{self.BASE_URL}/{model_name}"
        
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                url, 
                headers=self.headers, 
                json={"inputs": prompt}
            )
            
            if response.status_code == 404:
                raise Exception(f"Model not available: {model_name}. Try another model.")
            elif response.status_code == 503:
                raise Exception("Model loading, try again in 30s")
            elif response.status_code != 200:
                raise Exception(f"HF API Error ({response.status_code}): {response.text}")
            
            return response.content
    
    async def edit_image(self, prompt: str, image_bytes: bytes, model: Optional[str] = None) -> bytes:
        # Image editing via img2img pipeline
        model_name = model or "runwayml/stable-diffusion-v1-5"
        url = f"{self.BASE_URL}/{model_name}"
        
        img_b64 = base64.b64encode(image_bytes).decode()
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "image": img_b64,
                        "num_inference_steps": 20,
                        "guidance_scale": 7.5
                    }
                }
            )
            if response.status_code != 200:
                raise Exception(f"HF API Error: {response.text}")
            return response.content
    
    async def generate_song(self, prompt: str, style: str = "", model: Optional[str] = None) -> bytes:
        # ✅ MusicGen - check if available
        model_name = model or "facebook/musicgen-small"
        url = f"{self.BASE_URL}/{model_name}"
        
        full_prompt = f"{style} {prompt}".strip() if style else prompt
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={"inputs": full_prompt}
            )
            
            if response.status_code == 404:
                # Fallback to alternative audio model
                raise Exception(f"Model not available: {model_name}. MusicGen may not be on hf-inference.")
            elif response.status_code != 200:
                raise Exception(f"HF API Error: {response.text}")
            
            return response.content
    
    def get_available_presets(self) -> list:
        return [
            {"id": "lofi", "name": "Lo-Fi Beats"},
            {"id": "pop", "name": "Pop Music"},
            {"id": "ambient", "name": "Ambient"},
            {"id": "rock", "name": "Rock"},
            {"id": "jazz", "name": "Jazz"},
            {"id": "electronic", "name": "Electronic"},
        ]

hf_client = HFClient()

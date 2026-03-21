import httpx
from config import settings
from typing import Optional
import base64

class HFClient:
    # HF Inference (for images)
    HF_BASE_URL = "https://router.huggingface.co/hf-inference/models"
    
    # Pollinations.ai (FREE - no token needed for audio)
    POLLINATIONS_AUDIO_URL = "https://pollinations.ai/p/"
    
    def __init__(self, api_token: Optional[str] = None):
        self.token = api_token or settings.HF_API_TOKEN
        self.headers = {}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
        self.headers["Content-Type"] = "application/json"
    
    async def generate_image(self, prompt: str, model: Optional[str] = None) -> bytes:
        model_name = model or "black-forest-labs/FLUX.1-schnell"
        url = f"{self.HF_BASE_URL}/{model_name}"
        
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(url, headers=self.headers, json={"inputs": prompt})
            if response.status_code == 404:
                fallback = "stabilityai/stable-diffusion-xl-base-1.0"
                url = f"{self.HF_BASE_URL}/{fallback}"
                response = await client.post(url, headers=self.headers, json={"inputs": prompt})
            if response.status_code == 503:
                raise Exception("Model loading, try again in 30s")
            elif response.status_code != 200:
                raise Exception(f"HF API Error ({response.status_code}): {response.text}")
            return response.content
    
    async def edit_image(self, prompt: str, image_bytes: bytes, model: Optional[str] = None) -> bytes:
        model_name = model or "stabilityai/stable-diffusion-xl-base-1.0"
        url = f"{self.HF_BASE_URL}/{model_name}"
        img_b64 = base64.b64encode(image_bytes).decode()
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, headers=self.headers, json={
                "inputs": prompt,
                "parameters": {"image": img_b64, "num_inference_steps": 20, "guidance_scale": 7.5}
            })
            if response.status_code != 200:
                raise Exception(f"HF API Error: {response.text}")
            return response.content
    
    async def generate_song(self, prompt: str, style: str = "", model: Optional[str] = None) -> bytes:
        """
        Generate audio using Pollinations.ai (FREE, no token required)
        Alternative to MusicGen which is not on free HF inference
        """
        # Clean prompt for URL
        clean_prompt = f"{style} {prompt}".strip().replace(" ", "_")
        url = f"{self.POLLINATIONS_AUDIO_URL}{clean_prompt}.mp3"
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.get(url)
            if response.status_code == 200 and len(response.content) > 1000:
                return response.content
            else:
                # Fallback: Try Suno-style prompt
                alt_url = f"{self.POLLINATIONS_AUDIO_URL}{clean_prompt}_instrumental.mp3"
                response = await client.get(alt_url)
                if response.status_code == 200 and len(response.content) > 1000:
                    return response.content
        
        raise Exception("Audio generation failed. Try a different prompt.")
    
    def get_available_presets(self) -> list:
        return [
            {"id": "lofi", "name": "Lo-Fi Beats"},
            {"id": "pop", "name": "Pop Music"},
            {"id": "ambient", "name": "Ambient"},
            {"id": "rock", "name": "Rock"},
            {"id": "jazz", "name": "Jazz"},
            {"id": "electronic", "name": "Electronic"},
            {"id": "cinematic", "name": "Cinematic"},
            {"id": "gaming", "name": "Gaming Music"},
        ]

hf_client = HFClient()

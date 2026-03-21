import httpx
from config import settings
from typing import Optional
import base64

class HFClient:
    BASE_URL = "https://api-inference.huggingface.co/models"
    
    def __init__(self, api_token: Optional[str] = None):
        self.token = api_token or settings.HF_API_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}" if self.token else ""}
    
    async def generate_image(self, prompt: str, model: Optional[str] = None) -> bytes:
        model_name = model or settings.HF_IMAGE_MODEL
        url = f"{self.BASE_URL}/{model_name}"
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers=self.headers, json={"inputs": prompt})
            if response.status_code != 200:
                if response.status_code == 503:
                    raise Exception("Model loading, try again in 30s")
                raise Exception(f"HF API Error: {response.text}")
            return response.content
    
    async def edit_image(self, prompt: str, image_bytes: bytes, model: Optional[str] = None) -> bytes:
        model_name = model or "runwayml/stable-diffusion-v1-5"
        url = f"{self.BASE_URL}/{model_name}"
        img_b64 = base64.b64encode(image_bytes).decode()
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, headers=self.headers, json={"inputs": prompt, "parameters": {"image": img_b64, "num_inference_steps": 20, "guidance_scale": 7.5}})
            if response.status_code != 200:
                raise Exception(f"HF API Error: {response.text}")
            return response.content
    
    async def generate_song(self, prompt: str, style: str = "", model: Optional[str] = None) -> bytes:
        model_name = model or settings.HF_SONG_MODEL
        url = f"{self.BASE_URL}/{model_name}"
        full_prompt = f"{style} {prompt}".strip() if style else prompt
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(url, headers=self.headers, json={"inputs": full_prompt})
            if response.status_code != 200:
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

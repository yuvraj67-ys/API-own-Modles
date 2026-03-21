import httpx
from config import settings
from typing import Optional, Union
import base64
import io

class HFClient:
    """Free Hugging Face Inference API client"""
    
    BASE_URL = "https://api-inference.huggingface.co/models"
    
    def __init__(self, api_token: Optional[str] = None):
        self.token = api_token or settings.HF_API_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}" if self.token else "",
            "Content-Type": "application/json"
        }
    
    async def generate_image(self, prompt: str, model: Optional[str] = None) -> bytes:
        """Generate image using Stable Diffusion"""
        model_name = model or settings.HF_IMAGE_MODEL
        url = f"{self.BASE_URL}/{model_name}"
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={"inputs": prompt}
            )
            
            if response.status_code != 200:
                # Handle model loading state
                if response.status_code == 503:
                    raise Exception("Model is loading, please try again in 30 seconds")
                raise Exception(f"HF API Error: {response.text}")
            
            return response.content  # Returns PNG bytes
    
    async def edit_image(self, prompt: str, image_bytes: bytes, model: Optional[str] = None) -> bytes:
        """Edit image using img2img or inpainting"""
        # Using stable-diffusion-img2img for editing
        model_name = model or "runwayml/stable-diffusion-v1-5"
        url = f"{self.BASE_URL}/{model_name}"
        
        # Convert image to base64 for API
        import base64
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
        """Generate music using MusicGen"""
        model_name = model or settings.HF_SONG_MODEL
        url = f"{self.BASE_URL}/{model_name}"
        
        # Combine prompt and style
        full_prompt = f"{style} {prompt}".strip() if style else prompt
        
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(
                url,
                headers=self.headers,
                json={"inputs": full_prompt}
            )
            
            if response.status_code != 200:
                raise Exception(f"HF API Error: {response.text}")
            
            return response.content  # Returns MP3/WAV bytes
    
    def get_available_presets(self) -> list:
        """Return song style presets"""
        return [
            {"id": "lofi", "name": "Lo-Fi Beats", "desc": "Chill relaxing beats"},
            {"id": "pop", "name": "Pop Music", "desc": "Upbeat popular style"},
            {"id": "ambient", "name": "Ambient", "desc": "Atmospheric soundscapes"},
            {"id": "rock", "name": "Rock", "desc": "Electric guitar driven"},
            {"id": "jazz", "name": "Jazz", "desc": "Smooth jazz improvisation"},
            {"id": "electronic", "name": "Electronic", "desc": "Synth and digital beats"},
        ]

# Singleton instance
hf_client = HFClient()
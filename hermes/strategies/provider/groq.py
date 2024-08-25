import os
import requests
from typing import Dict, Any
from .base import ProviderStrategy

class GroqProviderStrategy(ProviderStrategy):
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.base_url = "https://api.groq.com/openai/v1/audio/transcriptions"

    def transcribe(self, audio_data: bytes, params: Dict[str, Any] = None) -> str:
        params = params or {}
        model = params.get("model", "distil-whisper-large-v3-en")
        response_format = params.get("response_format", "text")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        files = {
            "file": ("audio.wav", audio_data, "audio/wav"),
        }

        data = {
            "model": model,
            "response_format": response_format,
            "temperature": 0,
            "language": "en",
        }

        response = requests.post(self.base_url, headers=headers, files=files, data=data)
        response.raise_for_status()

        return response.text

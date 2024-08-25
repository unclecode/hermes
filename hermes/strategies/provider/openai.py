import os
import requests
from typing import Dict, Any
from .base import ProviderStrategy

class OpenAIProviderStrategy(ProviderStrategy):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.base_url = "https://api.openai.com/v1/audio/transcriptions"

    def transcribe(self, audio_data: bytes, params: Dict[str, Any] = None) -> str:
        params = params or {}
        model = params.get("model", "whisper-1")
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
        }

        response = requests.post(self.base_url, headers=headers, files=files, data=data)
        response.raise_for_status()

        return response.text if response_format == "text" else response.json()